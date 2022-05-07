import discord
from discord import Interaction
from discord.ext import commands
from discord import app_commands
from typing import Literal

from utils.checks import cooldown_for_everyone_but_me
from utils import Cog
from utils.emojis import LATTE_EMOJI

class Mod(Cog):
    """Moderator commands"""

    @property
    def display_emoji(self) -> discord.Emoji:
        return str(LATTE_EMOJI.MOD)
        # return self.bot.get_emoji(970838278318211133)

    @app_commands.command()
    @app_commands.describe(amount='The amount of messages to delete', type='Type of messages to delete')
    @app_commands.checks.has_permissions(manage_messages=True, read_message_history=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True, read_message_history=True)
    @app_commands.default_permissions(manage_messages=True, read_message_history=True)
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def clear(
        self,
        interaction: Interaction,
        amount: int,
        type: Literal['BOT', 'Attachments', 'Embed'] = None) -> None:  
        """Clear the messages of the channel"""
        await interaction.response.defer(ephemeral=True)

        if amount < 1:
            raise RuntimeError('Amount must be greater than 0')

        if amount > 100:
            raise RuntimeError('Amount must be less than 100')

        if type == 'BOT':
            deleted = await interaction.channel.purge(limit=amount, check=lambda m: m.author.bot)
        elif type == 'Attachments':
            deleted = await interaction.channel.purge(limit=amount, check=lambda m: m.attachments)
        elif type == 'Embed':
            deleted = await interaction.channel.purge(limit=amount, check=lambda m: m.embeds)
        else:
            deleted =  await interaction.channel.purge(limit=amount)
        embed = discord.Embed(
            description=f"{interaction.channel.mention} : `{len(deleted)}` - messages were cleared",
            color=self.bot.theme
        )
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Mod(bot))