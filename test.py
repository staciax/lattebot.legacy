# Standard
import os
import traceback
from discord import Interaction
from discord.app_commands import (
    AppCommandError
)
import logging

# Local
from utils import Latte_Bot

logging.basicConfig(level=logging.INFO, format=f'%(asctime)s:%(levelname)s:%(name)s: %(message)s')

os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
os.environ['JISHAKU_HIDE'] = 'True'

if __name__ == '__main__':
    
    bot = Latte_Bot()
    bot.command_prefix = '+'

    @bot.tree.error
    async def tree_error_handler(interaction: Interaction, error: AppCommandError) -> None:
        """ Handles errors for all application commands associated with this CommandTree."""

        traceback.print_exception(type(error), error, error.__traceback__)

        if interaction is not None:
            print(interaction.command.name)

    bot.run(os.getenv('DISCORD_TOKEN_TEST'))