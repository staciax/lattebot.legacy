import discord
import time

from discord import ui, Interaction, SelectOption, Member, User
from discord.ext import commands
from typing import List, Any, Union
from .useful import LatteEmbed
from .utils import get_dominant_color

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
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allowing the context author to interact with the view"""
        author = self.interaction.user
        if await self.bot.is_owner(interaction.user):
            return True
        if interaction.user != author:
            content = f"Only `{author}` can use this. If you want to use it, use `/{self.interaction.command.name}`"
            embed = LatteEmbed.to_error(description=content)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

class AvatarView(ui.View):
    def __init__(self, interaction: Interaction, member: Union[Member, User] ) -> None:
        super().__init__(timeout=60)
        self.interaction = interaction
        self.member = member
        self.avatar_url = self.member.avatar
        self.display_url = self.member.display_avatar if self.member.avatar != self.member.display_avatar else None
        self.avatar_embed: discord.Embed = None
        self.display_embed: discord.Embed = None
        self.fill_items()

    async def on_timeout(self) -> None:
        self.remove_item(self.avatar_select)
        await self.interaction.edit_original_message(view=self)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user != self.interaction.user:
            await interaction.response.send_message(f"Only `{self.interaction.user.display_name}` can use this.", ephemeral=True)
            return False
        return True
    
    def fill_items(self, select=None):
        self.clear_items()
        
        if self.display_url is not None:
            self.add_item(self.avatar_select)

        if select == 'avatar':
            self.avatar_url_button()
        elif select == 'display':
            self.display_url_button()

    def avatar_url_button(self) -> None:
        self.add_item(ui.Button(label="Avatar URL", url=self.avatar_url.url, row=1))
    
    def display_url_button(self) -> None:
        self.add_item(ui.Button(label="Server avatar URL", url=self.display_url.url, row=1))

    @ui.select(placeholder="Select avatar", row=0, options=[
        SelectOption(label='Avatar', value='avatar'),
        SelectOption(label='Server Avatar', value='display'),
    ])
    async def avatar_select(self, interaction: Interaction, select: ui.Select) -> None:
        self.fill_items(select.values[0])
        if select.values[0] == 'avatar':
            await interaction.response.edit_message(embed=self.avatar_embed, view=self)
        elif select.values[0] == 'display':
            await interaction.response.edit_message(embed=self.display_embed, view=self)
            
    def build_avatar_embed(self) -> discord.Embed:
        color = get_dominant_color(self.avatar_url.replace(format='png'))
        embed = discord.Embed(title= f"{self.interaction.user.name}'s Avatar:", color=color)
        embed.set_image(url=self.avatar_url) 
        self.avatar_embed = embed
        self.avatar_url_button()
        return embed

    def build_isplay_embed(self) -> discord.Embed:
        color = get_dominant_color(self.display_url.replace(format='png'))
        embed = discord.Embed(title=f"{self.interaction.user.name}'s Server avatar:", color=color)
        embed.set_image(url=self.display_url)
        self.display_embed = embed
        return embed

    async def start(self) -> None:
        embed = self.build_avatar_embed()
        await self.interaction.response.send_message(embed=embed, view=self)

class Confirm(discord.ui.View):
    def __init__(self, interaction: Interaction):
        super().__init__()
        self.value = None
        self.interaction = interaction

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        await interaction.response.send_message('This menus cannot be controlled by you, sorry!', ephemeral=True)
        return False

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        # await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        # await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()