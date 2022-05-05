import discord
from discord.ext import commands
from discord import app_commands

from utils.bot_base import Latte_Bot

class _context_menu(commands.Cog):
    def __init__(self, bot: Latte_Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='Cool Command Name',
            callback=self.my_cool_context_menu,
            # guild_ids=[...],
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    # You can add checks too
    @app_commands.checks.has_permissions(ban_members=True)
    async def my_cool_context_menu(self, interaction: discord.Interaction, message: discord.Message) -> None:
        await interaction.response.send_message('hello...')

async def setup(bot):
    await bot.add_cog(_context_menu(bot))