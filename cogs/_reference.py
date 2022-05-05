import discord
from discord.ext import commands
from discord import app_commands

from utils import Cog

async def owner_only(interaction: discord.Interaction) -> bool:
    return await interaction.client.is_owner(interaction.user)

def check_role(interaction: discord.Interaction) -> bool:
    role = interaction.client.get_guild(interaction.guild.id).get_role(123456)
    if role in interaction.author.roles:
        return True
    raise commands.CheckFailure

class _reference(Cog):

    @commands.Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__)

    @app_commands.command()
    @app_commands.checks.dynamic_cooldown(5, 60, app_commands.BucketType.channel)
    @app_commands.check(owner_only)
    async def testing(self, interaction: discord.Interaction):
        ...

async def setup(bot):
    await bot.add_cog(_reference(bot))