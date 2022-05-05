from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, Optional, TYPE_CHECKING, Awaitable
import discord
from discord import ui
from discord.ext import commands
from discord.ext.commands import Paginator as CommandPaginator
from discord.ext import menus

from .modal import BaseModal

if TYPE_CHECKING:
    from .bot_base import Latte_Bot

class BaseView(discord.ui.View):
    
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
            return await self.on_error(interaction, e, item)

class ViewAuthor(BaseView):
    def __init__(self, interaction: discord.Interaction, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.interaction = interaction
        self.bot: Latte_Bot = getattr(interaction, "client", interaction._state._get_client())
        self.is_command = interaction.command is not None
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allowing the context author to interact with the view"""
        
        author = self.interaction.user
        
        if await self.bot.is_owner(interaction.user):
            return True
        
        if interaction.user != author:
            bucket = self.cooldown.get_bucket(interaction.message)
            if not bucket.update_rate_limit():
                if self.is_command:
                    command = self.bot.get_command_signature(self.interaction.command)
                    content = f"Only `{author}` can use this. If you want to use it, use `{command}`"
                else:
                    content = f"Only `{author}` can use this."
                embed = discord.Embed(color=self.bot.theme, description=content)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

class LattePage(BaseView):
    def __init__(
        self,
        source: menus.PageSource,
        *,
        interaction: discord.Interaction,
        ephemeral:bool = False,
        check_embeds: bool = True,
        compact: bool = False,
    ):
        super().__init__()
        self.source: menus.PageSource = source
        self.check_embeds: bool = check_embeds
        self.interaction = interaction
        self.ephemeral = ephemeral
        self.bot: Latte_Bot = getattr(interaction, "client", interaction._state._get_client())
        self.current_page: int = 0
        self.compact: bool = compact
        self.input_lock = asyncio.Lock()
        self.prompter: Optional[LattePage.PagePrompt] = None
        self.message: Optional[discord.Message] = None
        self.clear_items()
        self.fill_items()

    class PagePrompt(BaseModal):
        page_number = ui.TextInput(label="Page Number", min_length=1, required=True)

        def __init__(self, view: LattePage):
            max_pages = view.source.get_max_pages()
            super().__init__(title=f"Go to page")
            # super().__init__(title=f"Pick a page from 1 to {max_pages}")
            self.page_number.label = f"Page Number (1-{max_pages})"
            self.page_number.max_length = len(str(max_pages))
            self.view = view
            self.max_pages = max_pages
            self.valid = False
            self.interaction = view.interaction

        async def interaction_check(self, interaction: discord.Interaction) -> Optional[bool]:
            # extra measures, there isn't a way for this to trigger.
            if interaction.user == self.interaction.user:
                return True

            await interaction.response.send_message("You can't fill up this modal.", ephemeral=True)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            value = self.page_number.value.strip()
            if value.isdigit() and 0 < (page := int(value)) <= self.max_pages:
                await self.view.show_checked_page(interaction, page - 1)
                self.view.reset_timeout()
                return

            def send(content: str) -> Awaitable[None]:
                return interaction.response.send_message(content, ephemeral=True)

            if not value.isdigit():
                if value.lower() == "cancel":
                    return

                await send(f"`{value}` is not a page number")
            else:
                await send(f"Please pick a number between 1 and {self.max_pages}. Not {value}")

    def fill_items(self) -> None:
        if not self.compact:
            self.numbered_page.row = 1
            self.stop_pages.row = 1

        if self.source.is_paginating():
            max_pages = self.source.get_max_pages()
            use_last_and_first = max_pages is not None and max_pages >= 2
            if use_last_and_first:
                self.add_item(self.go_to_first_page)  # type: ignore
            self.add_item(self.go_to_previous_page)  # type: ignore
            if not self.compact:
                self.add_item(self.go_to_current_page)  # type: ignore
            self.add_item(self.go_to_next_page)  # type: ignore
            if use_last_and_first:
                self.add_item(self.go_to_last_page)  # type: ignore
            if not self.compact:
                self.add_item(self.numbered_page)  # type: ignore
            self.add_item(self.stop_pages)  # type: ignore

    async def _get_kwargs_from_page(self, page: int) -> Dict[str, Any]:
        value = await discord.utils.maybe_coroutine(self.source.format_page, self, page)
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            return {'content': value, 'embed': None}
        elif isinstance(value, discord.Embed):
            return {'embed': value, 'content': None}
        else:
            return {}

    async def show_page(self, interaction: discord.Interaction, page_number: int) -> None:
        page = await self.source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(page_number)
        if kwargs:
            if interaction.response.is_done():
                if await self.interaction.original_message():
                    await self.interaction.edit_original_message(**kwargs, view=self)
            else:
                await interaction.response.edit_message(**kwargs, view=self)

    def _update_labels(self, page_number: int) -> None:
        self.go_to_first_page.disabled = page_number == 0
        if self.compact:
            max_pages = self.source.get_max_pages()
            self.go_to_last_page.disabled = max_pages is None or (page_number + 1) >= max_pages
            self.go_to_next_page.disabled = max_pages is not None and (page_number + 1) >= max_pages
            self.go_to_previous_page.disabled = page_number == 0
            return

        self.go_to_current_page.label = str(page_number + 1)
        self.go_to_previous_page.label = str(page_number)
        self.go_to_next_page.label = str(page_number + 2)
        self.go_to_next_page.disabled = False
        self.go_to_previous_page.disabled = False
        self.go_to_first_page.disabled = False

        max_pages = self.source.get_max_pages()
        if max_pages is not None:
            self.go_to_last_page.disabled = (page_number + 1) >= max_pages
            if (page_number + 1) >= max_pages:
                self.go_to_next_page.disabled = True
                self.go_to_next_page.label = '…'
            if page_number == 0:
                self.go_to_previous_page.disabled = True
                self.go_to_previous_page.label = '…'

    async def show_checked_page(self, interaction: discord.Interaction, page_number: int) -> None:
        max_pages = self.source.get_max_pages()
        try:
            if max_pages is None:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(interaction, page_number)
            elif max_pages > page_number >= 0:
                await self.show_page(interaction, page_number)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id in (self.bot.owner_id, self.interaction.user.id):
            return True
        await interaction.response.send_message('This pagination menu cannot be controlled by you, sorry!', ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        if await self.interaction.original_message():
            return await self.interaction.edit_original_message(view=None)
        
        if self.message:
            await self.message.edit(view=None)

    # async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item[Any]) -> None:
    #     print(f"Error in pagination menu: {error}")
    #     if interaction.response.is_done():
    #         await interaction.followup.send('An unknown error occurred, sorry', ephemeral=True)
    #     else:
    #         await interaction.response.send_message('An unknown error occurred, sorry', ephemeral=True)

    async def start(self, *, content: Optional[str] = None) -> None:
        if self.check_embeds and not self.interaction.channel.permissions_for(self.interaction.guild.me).embed_links:
            if self.interaction.response.is_done():
                await self.interaction.followup.send('Bot does not have embed links permission in this channel.', ephemeral=True)
            else:
                await self.interaction.response.send_message('Bot does not have embed links permission in this channel.', ephemeral=True)
            return

        ephemeral = self.ephemeral
        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        if content:
            kwargs.setdefault('content', content)
            
        self._update_labels(0)
        if self.interaction.response.is_done():
            self.message = await self.interaction.followup.send(**kwargs, view=self, ephemeral=ephemeral)
            return 
        await self.interaction.response.send_message(**kwargs, view=self, ephemeral=ephemeral)

    @discord.ui.button(label='≪', style=discord.ButtonStyle.grey)
    async def go_to_first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """go to the first page"""
        await self.show_page(interaction, 0)

    @discord.ui.button(label='Back', style=discord.ButtonStyle.blurple)
    async def go_to_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """go to the previous page"""
        await self.show_checked_page(interaction, self.current_page - 1)

    @discord.ui.button(label='Current', style=discord.ButtonStyle.grey, disabled=True)
    async def go_to_current_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label='Next', style=discord.ButtonStyle.blurple)
    async def go_to_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """go to the next page"""
        await self.show_checked_page(interaction, self.current_page + 1)

    @discord.ui.button(label='≫', style=discord.ButtonStyle.grey)
    async def go_to_last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """go to the last page"""
        # The call here is safe because it's guarded by skip_if
        await self.show_page(interaction, self.source.get_max_pages() - 1)

    @discord.ui.button(label='\N{RIGHTWARDS ARROW WITH HOOK} \u200b Go to page', style=discord.ButtonStyle.primary)
    async def numbered_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.prompter is None:
            self.prompter = self.PagePrompt(self)

        return await interaction.response.send_modal(self.prompter)

    @discord.ui.button(label='Quit', style=discord.ButtonStyle.red)
    async def stop_pages(self, interaction: discord.Interaction, button: discord.ui.Button):
        """stops the pagination session."""
        await interaction.response.defer()
        await interaction.delete_original_message()
        self.stop()
            

class FieldPageSource(menus.ListPageSource):
    """A page source that requires (field_name, field_value) tuple items."""

    def __init__(self, entries, *, per_page=12):
        super().__init__(entries, per_page=per_page)
        self.embed = discord.Embed(colour=discord.Colour.blurple())

    async def format_page(self, menu, entries):
        self.embed.clear_fields()
        self.embed.description = discord.Embed.Empty

        for key, value in entries:
            self.embed.add_field(name=key, value=value, inline=False)

        maximum = self.get_max_pages()
        if maximum > 1:
            text = f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)'
            self.embed.set_footer(text=text)

        return self.embed

class TextPageSource(menus.ListPageSource):
    def __init__(self, text, *, prefix='```', suffix='```', max_size=2000):
        pages = CommandPaginator(prefix=prefix, suffix=suffix, max_size=max_size - 200)
        for line in text.split('\n'):
            pages.add_line(line)

        super().__init__(entries=pages.pages, per_page=1)

    async def format_page(self, menu, content):
        maximum = self.get_max_pages()
        if maximum > 1:
            return f'{content}\nPage {menu.current_page + 1}/{maximum}'
        return content

class SimplePageSource(menus.ListPageSource):
    async def format_page(self, menu, entries):
        pages = []
        for index, entry in enumerate(entries, start=menu.current_page * self.per_page):
            pages.append(f'{index + 1}. {entry}')

        maximum = self.get_max_pages()
        if maximum > 1:
            footer = f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)'
            menu.embed.set_footer(text=footer)

        menu.embed.description = '\n'.join(pages)
        return menu.embed

class SimplePages(LattePage):
    """A simple pagination session reminiscent of the old Pages interface.
    Basically an embed with some normal formatting.
    """
    def __init__(self, entries, *, interaction: discord.Interaction, per_page: int = 12):
        super().__init__(SimplePageSource(entries, per_page=per_page), interaction=interaction)
        self.embed = discord.Embed(colour=discord.Colour.blurple())