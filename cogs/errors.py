from __future__ import annotations

import discord
import traceback
from discord import Interaction
from discord.ext import commands
from discord.app_commands import (
    AppCommandError,
    CommandInvokeError,
    CommandNotFound,
    MissingPermissions,
    BotMissingPermissions,
    CheckFailure,
    CommandSignatureMismatch,
    CommandOnCooldown
)
from typing import Union

from utils.bot_base import Latte_Bot

class ErrorHandler(commands.Cog):
    """Error handler"""

    def __init__(self, bot: Latte_Bot) -> None:
        self.bot = bot
        # setting the handler
        bot.tree.on_error = self.on_app_command_error
        bot.tree.interaction_check = self.interaction_check

    @property
    def display_emoji(self) -> discord.Emoji:
        return '<:valoranticon:974232643031937024>'

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
   
        if interaction.user.id == 240059262297047041:
            return True
            
        locale = interaction.locale
        if self.bot.dev_mode is True: 
            message = "❌ Bot is under maintenance. please wait"
            if str(locale) == 'th':
                message = "❌ บอทอยู่ระหว่างการปรับปรุง กรุณาลองใหม่อีกครั้งในภายหลัง"
            await interaction.response.send_message(message)
            return False
        return True

    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        """ Handles errors for all application commands associated with this CommandTree."""

        traceback.print_exception(type(error), error, error.__traceback__)

        error_unknown = "An unknown error occurred, sorry"
        if isinstance(error, CommandInvokeError) and not isinstance(error, (KeyError,ValueError,TypeError, IndexError, AttributeError)):
            error = error.original
        elif isinstance(error, Union[CommandNotFound, MissingPermissions, BotMissingPermissions]):
            error = error
        elif isinstance(error, CommandOnCooldown):
            error = error
        elif isinstance(error, Union[CommandSignatureMismatch, CommandNotFound]):
            error = "Sorry, but this command seems to be unavailable! Please try again later..."
        elif isinstance(error, CheckFailure):
            error = "You can't use this command."
        else:
            error = error_unknown
            traceback.print_exception(type(error), error, error.__traceback__)

        if interaction is not None:

            error_content = f'{str(error)[:1950]}' if len(str(error)) < 100 else error_unknown
            embed = discord.Embed(description=error_content, color=0xfe676e)
            if interaction.response.is_done():
                return await interaction.followup.send(embed=embed, ephemeral=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)

            # traceback log
            log_channel = self.bot.get_channel(970398611030548510)
            await log_channel.send(f"```py\n{traceback.format_exc()[:1950]}```")

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))