from __future__ import annotations

# Standard
import discord
from discord.ext import commands
from discord import app_commands, Interaction, ui
from discord.app_commands.checks import dynamic_cooldown

from typing import Any, Dict, List, Optional, Union, Literal
from datetime import datetime, timedelta, timezone

from utils.view import ViewAuthor
from utils.checks import cooldown_5s
from utils import Latte_Bot
from utils.emojis import LATTE_EMOJI

ignore_extensions = ['Owner', 'Jishaku', 'Events', 'Admin', 'Help', 'Testing', 'NotifySkin']

class FrontPage(discord.Embed):
    def __init__(self, bot: Latte_Bot):
        self.bot = bot
        emoji = LATTE_EMOJI
        super().__init__()
        self.color = bot.theme
        self.set_author(name=f'{bot.user.display_name} - Help', icon_url=bot.user.avatar)
        self.description = "Use **Selection** for more informations about a category.\n" \
            # + f"Total commands: `{len(bot.tree.get_commands())}`"
        self.add_field(
            name='\u200b',
            value=f'•{emoji.RAIDEN} Anime\n•{emoji.MISC} Misc',
            inline=True
        )
        self.add_field(
            name='\u200b',
            value=f'•🥳 Fun\n•{emoji.MIKU_MUSIC} Music',
            inline=True
        )
        self.add_field(
            name='\u200b',
            value=f'•{emoji.LOVE_NOTE} Infomatic\n•{emoji.GIFT_BLUE} Utility',
            inline=True
        )
        self.add_field(
            name='• Ext',
            value=f'•{emoji.VALORANT} Valorant',
            inline=True
        )

class HelpSelectMenu(ui.Select['HelpView']):
    def __init__(self, commands: dict[commands.Cog, list[commands.Command]], bot: Latte_Bot):
        super().__init__(
            placeholder='Select a category...',
            min_values=1,
            max_values=1,
            row=0,
        )
        self.commands: dict[commands.Cog, list[commands.Command]] = commands
        self.bot: Latte_Bot = bot
        self.index = FrontPage(bot)
        self.__fill_options()

    def __fill_options(self) -> None:
        self.add_option(
            label='Index',
            value='__index',
            emoji=str(LATTE_EMOJI.LATTE)
        )
        for cog, commands in sorted(self.commands.items(), key=lambda x: x[0].qualified_name):
            if not commands:
                continue
            description = cog.description.split('\n', 1)[0] or None
            emoji = getattr(cog, 'display_emoji', None)
            self.add_option(label=cog.qualified_name, value=cog.qualified_name, description=description, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        value = self.values[0]

        if value == '__index':
            self.view.clear_items()
            self.view.add_item(self)
            self.view.after_select = True
            await interaction.response.edit_message(embed=self.index, view=self.view)
        else:
            cog = self.bot.get_cog(value)
            if cog is None:
                await interaction.response.send_message('Somehow this category does not exist?', ephemeral=True)
                return

            commands = self.commands[cog]
            if not commands:
                await interaction.response.send_message('This category has no commands for you', ephemeral=True)
                return

            embeds = self.view.build_embeds(cog, commands)
            self.view.embeds = embeds
            await self.view.show_page(interaction, 0)

class HelpView(ViewAuthor):

    def __init__(self, interaction: Interaction, data: Dict[commands.Cog, List[commands.Command]]=None):
        super().__init__(timeout=90)
        self.interaction = interaction
        self.bot: Latte_Bot = getattr(interaction, "client", interaction._state._get_client())
        self.data = data
        self.current_page = 0
        self.embeds: List[discord.Embed] = []
        self.after_select = True
        self.clear_items()

    @ui.button(label='≪')
    async def first_page(self, interaction: Interaction,  button: ui.Button):
        await self.show_page(interaction, 0)

    @ui.button(label="Back", style=discord.ButtonStyle.blurple)
    async def back_page(self, interaction: Interaction,  button: ui.Button):
        await self.show_page(interaction, -1)

    @ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction: Interaction,  button: ui.Button):
        await self.show_page(interaction, +1)

    @ui.button(label='≫')
    async def last_page(self, interaction: Interaction,  button: ui.Button):
        last = len(self.embeds) - 1
        await self.show_page(interaction, last)

    def fill_items(self) -> None:
        if self.after_select:
            self.add_item(self.first_page)
            self.add_item(self.back_page)
            self.add_item(self.next_page)
            self.add_item(self.last_page)
            self.after_select = False

    def __verify_page(self, page_number: int):
        if page_number <= 1 and page_number != 0:
            page_number = self.current_page + page_number
        self.current_page = page_number

    async def show_page(self, interaction: Interaction, page_number: int, type_message='edit_message') -> None:
        try:
            self.__verify_page(page_number)
            self._update_buttons()
            self.fill_items()
            send_message = getattr(interaction.response, type_message)
            return await send_message(embed=self.embeds[self.current_page], view=self)
        except (IndexError, ValueError):
            return

    def default_embed(self, cog: commands.Cog) -> discord.Embed:
        embed = discord.Embed(title=f"{cog.display_emoji} {cog.qualified_name}", color=self.bot.theme,
        description=cog.description + '\n' or "No description provided" + '\n' )
        return embed

    def build_embeds(self, cog: commands.Cog, commands: List[app_commands.Command, app_commands.Group]) -> List[discord.Embed]:
        embeds = []

        embed = self.default_embed(cog)
        for command in commands:                
            name = f'{command.qualified_name}'
            # embed.description += f'\n<:bot_commands:904565707981852723> **{name}** - `{command.description}`'
            embed.description += f'\n`/{name}` - {command.description.lower()}'
            # embed.add_field(name='<:bot_commands:904565707981852723> %s' % name, value=command.description, inline=False)
            
            # if isinstance(command, app_commands.Group):
            #     commands_walk = sorted(command.walk_commands(), key=lambda c: c.name)
            #     for sub in commands_walk:
            #         signature = f'{name} {sub.name}'
            #         embed.add_field(name='<:bot_commands:904565707981852723> %s' % signature, value=sub.description, inline=False)
            #         if len(embed.fields) == 5:
            #             embeds.append(embed)
            #             embed = self.default_embed(cog, len(commands))
            
            if isinstance(command, app_commands.Group):
                commands_walk = sorted(command.walk_commands(), key=lambda c: c.name)
                for sub in commands_walk:
                    signature = f'`/{sub.qualified_name}`'
                    # embed.description += f'\n<:bot_commands:904565707981852723> **{signature}** - `{sub.description}`'
                    embed.description += f'\n{signature} - {sub.description.lower()}'

                    if len(embed.description.splitlines()) == 8:
                        embeds.append(embed)
                        embed = self.default_embed(cog)
            
            if len(embed.description.splitlines()) == 8:
                embeds.append(embed)
                embed = self.default_embed(cog)
            # if len(embed.fields) == 5:
            #     embeds.append(embed)
            #     embed = self.default_embed(cog, len(commands))

        if len(embed.description.splitlines()) > 0:
            embeds.append(embed)
        
        return embeds

    def _update_buttons(self):
        page = self.current_page
        total = len(self.embeds) - 1
        self.next_page.disabled = page == total
        self.back_page.disabled = page == 0
        self.first_page.disabled = page == 0
        self.last_page.disabled = page == total

    async def on_timeout(self) -> None:
        self.clear_items()
        support_emoji = LATTE_EMOJI.LATTE_SUPPORT
        latte_emoji = LATTE_EMOJI.LATTE_ICON
        
        self.add_item(ui.Button(label='ꜱᴜᴘᴘᴏʀᴛ ꜱᴇʀᴠᴇʀ', url=self.bot.latte_supprt_url, emoji=str(support_emoji)))
        self.add_item(ui.Button(label='ɪɴᴠɪᴛᴇ ᴍᴇ', url=self.bot.invite_url, emoji=str(latte_emoji)))
        await self.interaction.edit_original_message(view=self)

    async def start(self):
        self.add_item(HelpSelectMenu(self.data, self.bot))
        await self.interaction.response.send_message(embed=FrontPage(self.bot), view=self)
    
    async def start_cog(self, cog: commands.Cog, all_commands: List[app_commands.Command, app_commands.Group]):
        self.embeds = self.build_embeds(cog, all_commands)
        await self.show_page(self.interaction, 0, 'send_message')
        
class HelpCommand:

    def __init__(self, interaction: Interaction) -> None:
        self.bot: Latte_Bot = getattr(interaction, "client", interaction._state._get_client())
        self.interaction = interaction
    
    async def send_error_message(self, error: str):
        raise RuntimeError(error)

    def get_bot_all_commands(self) -> List[app_commands.Command, app_commands.Group]:
        bot = self.bot
        all_commands = {}
        for name in bot.cogs:
            if not name in ignore_extensions:
                cog = bot.get_cog(name)
                commands = cog.__cog_app_commands__
                commands = sorted(commands, key=lambda c: c.qualified_name)
                assert cog is not None
                all_commands[cog] = commands
            
        return all_commands
        
    async def send_bot_help(self, all_commands: List[commands.Cog, List[app_commands.Command, app_commands.Group]]):
        view = HelpView(self.interaction, all_commands)
        await view.start()
    
    async def send_cog_help(self, cog: commands.Cog):
        view = HelpView(self.interaction)
        await view.start_cog(cog, cog.__cog_app_commands__)

    async def command_callback(self, category: str = None):        
        
        if category is None:
            all_commands = self.get_bot_all_commands()
            return await self.send_bot_help(all_commands)

        cog = self.bot.get_cog(category)
        if cog is not None:
            return await self.send_cog_help(cog)
        
        await self.send_error_message("Category not found")
    
class Help(commands.Cog):
    def __init__(self, bot: Latte_Bot):
        self.bot = bot

    @app_commands.command(name='help')
    @app_commands.describe(category='Choose a category to get more informations about it.')
    @dynamic_cooldown(cooldown_5s)
    async def help_(
        self,
        interaction: Interaction,
        category: str = None
    ):  
        """Help"""
        Help = HelpCommand(interaction)
        await Help.command_callback(category)

    @help_.autocomplete('category')
    async def category_autocomplete(
        self,
        interaction: Interaction,
        current: str
    ) -> List[app_commands.Choice[str]]:

        mapping = [
            cog.qualified_name
            for cog in sorted(self.bot.cogs.values(), key=lambda c: c.qualified_name, reverse=False) if cog.qualified_name not in ignore_extensions
        ]
        return [
            app_commands.Choice(name=name, value=name)
            for name in mapping if current.lower() in name.lower()
        ]

async def setup(bot):
    await bot.add_cog(Help(bot))