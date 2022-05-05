from __future__ import annotations

import asyncio
import contextlib
import inspect
import time

from copy import copy
from enum import Enum
from functools import partial
from typing import (TYPE_CHECKING, Any, AsyncGenerator, Awaitable, Callable, Dict, Iterable, List, Optional, Type,
                    TypeVar, Union)

import asyncpg
import discord

from discord import ui
from discord import Interaction
from discord.ext import commands
from discord.ext import menus

from utils.context_managers import UserLock
from utils.modal import BaseModal
from utils.useful import LatteEmbed

if TYPE_CHECKING:
    from .bot_base import LatteBot

T = TypeVar("T")

InteractionCallback = Callable[[discord.Interaction], Awaitable[None]]

class BaseButton(ui.Button):
    def __init__(self, *, style: Optional[discord.ButtonStyle], selected: Union[int, str] = "",
                 row: Optional[int] = None, label: Optional[str] = None, stay_active: bool = False, **kwargs: Any):
        super().__init__(style=style, label=label or selected, row=row, **kwargs)
        self.selected = selected
        self.stay_active = stay_active

    async def callback(self, interaction: discord.Interaction) -> None:
        raise NotImplementedError

# types are redefined for better typing experience. ParamSpec isn't helpful here since it can't get kwargs from top
# level
def button(*, label: Optional[str] = None, custom_id: Optional[str] = None, disabled: bool = False,
           style: discord.ButtonStyle = discord.ButtonStyle.secondary,
           emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None, row: Optional[int] = None,
           stay_active: bool = False) -> Callable[[T], T]:
    """
    The only purpose of this is adding custom `stay_active` kwarg that prevents button from being deactivated by page
    bounds checks
    """
    def decorator(func: T) -> T:
        wrapped = ui.button(
            label=label,
            custom_id=custom_id,
            disabled=disabled,
            style=style,
            emoji=emoji,
            row=row,
        )(func)
        wrapped.__discord_ui_model_type__ = BaseButton
        wrapped.__discord_ui_model_kwargs__["stay_active"] = stay_active

        return wrapped

    return decorator

class BaseView(ui.View):
    def reset_timeout(self) -> None:
        self.set_timeout(time.monotonic() + self.timeout)

    def set_timeout(self, new_time: float) -> None:
        self._View__timeout_expiry = new_time

    async def _scheduled_task(self, item: discord.ui.item, interaction: discord.Interaction):
        try:
            if self.timeout:
                self.__timeout_expiry = time.monotonic() + self.timeout

            allow = await self.interaction_check(interaction)
            if not allow:
                return

            await item.callback(interaction)

            if not interaction.response._responded:
                await interaction.response.defer()
        except Exception as e:
            return await self.on_error(e, item, interaction)

class ViewAuthor(BaseView):
    def __init__(self, bot: commands.Bot, interaction: Interaction, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.interaction = interaction
        self.is_command = interaction.command is not None
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Only allowing the context author to interact with the view"""
    
        if await self.bot.is_owner(interaction.user):
            return True

        if interaction.user != self.interaction.user:
            bucket = self.cooldown.get_bucket(interaction.message)
            if not bucket.update_rate_limit():
                if self.is_command:
                    command = self.bot.get_command_signature(interaction, interaction.command)
                    content = f"Only `{self.interaction.user}` can use this. If you want to use it, use `{command}`"
                else:
                    content = f"Only `{self.interaction.user}` can use this."
                embed = LatteEmbed.to_error(description=content)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

class InteractionPages(BaseView):
    def __init__(self, source, generate_page: bool = False):
        super().__init__(timeout=120)
        self._source = source
        self._generate_page = generate_page
        self.interaction = None
        self.message = None
        self.current_page = 0
        self.current_button = None
        self.current_interaction = None
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)
        self.prompter: Optional[InteractionPages.PagePrompt] = None

    class PagePrompt(BaseModal):
        page_number = ui.TextInput(label="Page Number", min_length=1, required=True)

        def __init__(self, view: InteractionPages):
            max_pages = view._source.get_max_pages()
            super().__init__(title=f"Pick a page from 1 to {max_pages}")
            self.page_number.max_length = len(str(max_pages))
            self.view = view
            self.max_pages = max_pages
            self.valid = False
            self.interaction = view.interaction

        async def interaction_check(self, interaction: discord.Interaction) -> Optional[bool]:
            # extra measures, there isn't a way for this to trigger.
            if interaction.user == self.ctx.author:
                return True

            await interaction.response.send_message("You can't fill up this modal.", ephemeral=True)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            value = self.page_number.value.strip()
            if value.isdigit() and 0 < (page := int(value)) <= self.max_pages:
                await self.view.show_checked_page(page - 1)
                self.view.reset_timeout()
                return

            def send(content: str) -> Awaitable[None]:
                return interaction.response.send_message(content, ephemeral=True)

            if not value.isdigit():
                if value.lower() == "cancel":
                    return

                await send(f"{value} is not a page number")
            else:
                await send(f"Please pick a number between 1 and {self.max_pages}. Not {value}")

    def stop(self) -> None:
        if self.prompter:
            self.prompter.stop()

        super().stop()

    async def selecting_page(self, interaction: discord.Interaction) -> Awaitable[None]:
        if self.prompter is None:
            self.prompter = self.PagePrompt(self)

        return await interaction.response.send_modal(self.prompter)

    async def start(self, interaction: Interaction) -> None:
        self.interaction = interaction
        self.message = await self.send_initial_message(interaction, interaction.channel)

    def add_item(self, item: ui.Item) -> None:
        coro = copy(item.callback)
        item.callback = partial(self.handle_callback, coro)
        super().add_item(item)

    async def handle_callback(self, coro: Callable[[ui.Button, discord.Interaction], Awaitable[None]],
                              button: ui.Button, interaction: discord.Interaction, /) -> None:
        self.current_button = button
        self.current_interaction = interaction
        await coro(button, interaction)

    @button(emoji='<:before_fast_check:754948796139569224>', style=discord.ButtonStyle.blurple)
    async def first_page(self, _: ui.Button, __: discord.Interaction) -> None:
        await self.show_page(0)

    @button(emoji='<:before_check:754948796487565332>', style=discord.ButtonStyle.blurple)
    async def before_page(self, _: ui.Button, __: discord.Interaction) -> None:
        await self.show_checked_page(self.current_page - 1)

    @button(emoji='<:stop_check:754948796365930517>', style=discord.ButtonStyle.blurple)
    async def stop_page(self, _: ui.Button, __: discord.Interaction) -> None:
        self.stop()
        await self.message.delete(delay=0)

    @button(emoji='<:next_check:754948796361736213>', style=discord.ButtonStyle.blurple)
    async def next_page(self, _: ui.Button, __: discord.Interaction) -> None:
        await self.show_checked_page(self.current_page + 1)

    @button(emoji='<:next_fast_check:754948796391227442>', style=discord.ButtonStyle.blurple)
    async def last_page(self, _: ui.Button, __: discord.Interaction) -> None:
        await self.show_page(self._source.get_max_pages() - 1)

    @button(label="Select Page", style=discord.ButtonStyle.gray, stay_active=True)
    async def select_page(self, _: ui.Button, interaction: discord.Interaction) -> None:
        await self.selecting_page(interaction)

    async def _get_kwargs_from_page(self, page: Any) -> Dict[str, Any]:
        value = await super()._get_kwargs_from_page(page)
        self.format_view()
        if 'view' not in value:
            value.update({'view': self})
        value.update({'allowed_mentions': discord.AllowedMentions(replied_user=False)})
        return value

    def format_view(self) -> None:
        for i, b in enumerate(self.children):
            b.disabled = any(
                [
                    self.current_page == 0 and i < 2,
                    self.current_page == self._source.get_max_pages() - 1
                        and i > 2 and not getattr(b, "stay_active", False)
                ]
            )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        return False

    async def on_timeout(self) -> None:
        ...
        # await self.message.delete(delay=0)