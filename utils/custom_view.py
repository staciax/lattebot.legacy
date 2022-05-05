from __future__ import annotations

from discord import Interaction
import asyncio
import contextlib
import inspect
import os
import time
from copy import copy
from functools import partial
from typing import (TYPE_CHECKING, Any, AsyncGenerator, Callable, Coroutine,
                    Dict, Iterable, Optional, Tuple, Type, Union, Awaitable)

import discord
from discord import ui
from discord.ext import commands

from utils.context_managers import UserLock

from utils.useful import RenlyEmbed

# if TYPE_CHECKING:
#     from src.context import LatteContext

class BaseButton(ui.Button):
    def __init__(self, *, style: discord.ButtonStyle, selected: Union[int, str], row: int,
                 label: Optional[str] = None, **kwargs: Any):
        super().__init__(style=style, label=label or selected, row=row, **kwargs)
        self.selected = selected

    async def callback(self, interaction: discord.Interaction) -> None:
        raise NotImplementedError

class BaseView(ui.View):
    def reset_timeout(self):
        self.set_timeout(time.monotonic() + self.timeout)

    def set_timeout(self, new_time):
        self._View__timeout_expiry = new_time

class CallbackView(BaseView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for b in self.children:
            self.wrap(b)

    def wrap(self, b):
        callback = b.callback
        b.callback = partial(self.handle_callback, callback, b)

    async def handle_callback(self, callback, item, interaction):
        pass

    def add_item(self, item: ui.Item) -> None:
        self.wrap(item)
        super().add_item(item)

class ViewAuthor(BaseView):
    def __init__(self, ctx, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.context = ctx
        self.is_command = ctx.command is not None
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allowing the context author to interact with the view"""
        ctx = self.context
        author = ctx.author
        if await ctx.bot.is_owner(interaction.user):
            return True
        if interaction.user != author:
            bucket = self.cooldown.get_bucket(ctx.message)
            if not bucket.update_rate_limit():
                if self.is_command:
                    command = ctx.bot.get_command_signature(ctx, ctx.command)
                    content = f"Only `{author}` can use this. If you want to use it, use `{command}`"
                else:
                    content = f"Only `{author}` can use this."
                embed = RenlyEmbed.to_error(description=content)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

class ConfirmView(ViewAuthor, CallbackView):
    """ConfirmView literally handles confirmation where it asks the user at start() and returns a Tribool"""
    def __init__(self, ctx, *, delete_after: Optional[bool] = False, message_error=None):
        super().__init__(ctx)
        self.result = None
        self.message = None
        self.delete_after = delete_after
        self.message_error = message_error or "I'm waiting for your confirm response. You can't run another command."

    async def handle_callback(self, callback, item, interaction):
        self.result = await callback(interaction)
        if not interaction.response.is_done():
            await interaction.response.defer()
        self.stop()

    async def send(self, content: str, **kwargs: Any) -> Awaitable[None]:
        return await self.start(content=content, **kwargs)

    async def start(self, message: Optional[discord.Message] = None, **kwargs: Any) -> Optional[bool]:
        self.message = message or await self.context.send(view=self, **kwargs)

        lock = UserLock(self.context.author, self.message_error)
        async with lock(self.context.bot):
            await self.wait()

        if not self.delete_after:
            for x in self.children:
                x.disabled = True
            coro = self.message.edit_original_message(view=self)
        else:
            coro = self.message.delete()

        with contextlib.suppress(discord.HTTPException):
            await coro
        return self.result

    async def confirmed(self, interaction: Interaction, button: ui.Button):
        pass

    async def denied(self, interaction: Interaction, button: ui.Button):
        pass

    @ui.button(emoji="<:checkmark:753619798021373974>", label="Confirm", style=discord.ButtonStyle.green)
    async def confirmed_action(self, interaction: Interaction, button: ui.Button):
        await self.confirmed(button, interaction)
        return True

    @ui.button(emoji="<:crossmark:753620331851284480>", label="Cancel", style=discord.ButtonStyle.danger)
    async def denied_action(self, interaction: Interaction, button: ui.Button):
        await self.denied(button, interaction)
        return False

command_cooldown = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user)

class ButtonView(ViewAuthor, CallbackView):
    @ui.button(label='Re-run', style=discord.ButtonStyle.blurple)
    async def on_run(self, interaction: Interaction, button: ui.Button) -> None:
        if not (retry := command_cooldown.update_rate_limit(self.context.message)):
            await interaction.response.edit_message(view=None)
            new_message = await self.context.fetch_message(self.context.message.id)
            new_message._edited_timestamp = discord.utils.utcnow() # take account cooldown
            await self.context.reinvoke(message=new_message)
        else:
            raise commands.CommandOnCooldown(command_cooldown._cooldown, retry, command_cooldown._type)

    @ui.button(label='Delete', style=discord.ButtonStyle.danger)
    async def on_delete(self, interaction: Interaction, button: ui.Button) -> None:
        await interaction.message.delete(delay=0)

    async def handle_callback(self, callback, button: ui.Button, interaction: Interaction) -> None:
        try:
            await callback(interaction)
        except commands.CommandOnCooldown as cooldown:
            await interaction.response.send_message(
                content=f"Don't spam the button. You're on cooldown. Retry after: `{cooldown.retry_after:.2f}`",
                ephemeral=True
            )
        else:
            self.stop()