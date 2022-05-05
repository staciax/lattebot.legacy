import discord
from discord import app_commands
from discord.ext import commands

from typing import Optional
from utils import Latte_Bot

MY_GUILD = discord.Object(id=...)

class TagCommands(commands.Cog, name='Tags'):

    def __init__(self, bot: Latte_Bot) -> None:
        self.bot = bot

    @commands.hybrid_group(fallback='get')
    @app_commands.guilds(MY_GUILD)
    async def tag(self, ctx: commands.Context, name: str):
        await ctx.send(f'tag {name}')

    @tag.command()
    async def list(self, ctx: commands.Context, *, member: Optional[discord.Member] = None):
        await ctx.send(f'tag list {member}', ephemeral=True)

async def setup(bot) -> None:
    await bot.add_cog(TagCommands())