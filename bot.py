# Standard
import os
import traceback
import logging
import discord
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

from typing import Union, Literal

# Local
from utils import Latte_Bot
from utils import errors
from utils.latte_guild import LatteSupportVerifyView, LatteVerifyView

logging.basicConfig(level=logging.INFO, format=f'%(asctime)s:%(levelname)s:%(name)s: %(message)s')

os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
os.environ['JISHAKU_HIDE'] = 'True'

if __name__ == '__main__':
    
    bot = Latte_Bot()

    @bot.check
    def user_blacklisted(ctx) -> bool:
        if not bot.blacklist.get(ctx.author.id, None) or ctx.author.id == bot.owner_id:
            return True
        raise errors.UserBlacklisted

    @bot.check
    def tester_mode(ctx) -> bool:
        if not bot.tester or ctx.author.id == bot.owner_id:
            return True
        raise errors.BotTesting

    @bot.command()
    @commands.is_owner()
    async def sync(ctx: commands.Context, sync_type: str):
        
        ctx.typing()
        try:
            if sync_type == 'guild':
                guild = discord.Object(id=ctx.guild.id)
                bot.tree.copy_global_to(guild=guild)
                await bot.tree.sync(guild=guild)
                await ctx.reply(f"Synced guild !")
            elif sync_type == 'global':
                await bot.tree.sync()
                await ctx.reply(f"Synced global !")
        except discord.Forbidden:
            await ctx.send("Bot don't have permission to sync. : https://cdn.discordapp.com/attachments/939097458288496682/950613059150417970/IMG_3279.png")
        except discord.HTTPException:
            await ctx.send('Failed to sync.', delete_after=30)
    
    @bot.command()
    @commands.is_owner()
    async def unsync(ctx: commands.Context, sync_type: str):

        if bot.owner_id is None:
            if ctx.author.guild_permissions.administrator != True:
                await ctx.reply("You don't have **Administrator permission(s)** to run this command!", delete_after=30)
                return

        ctx.typing()
        try:
            if sync_type == 'guild':
                guild = discord.Object(id=ctx.guild.id)
                commands = bot.tree.get_commands(guild=guild)
                for command in commands:
                    bot.tree.remove_command(command, guild=guild)
                await bot.tree.sync(guild=guild)
                await ctx.reply(f"Un-Synced guild !")    
            elif sync_type == 'global':
                commands = bot.tree.get_commands()
                for command in commands:
                    bot.tree.remove_command(command)
                await bot.tree.sync()
                await ctx.reply(f"Un-Synced global !")
        except discord.Forbidden:
            await ctx.send("Bot don't have permission to unsync. : https://cdn.discordapp.com/attachments/939097458288496682/950613059150417970/IMG_3279.png")
        except discord.HTTPException:
            await ctx.send('Failed to unsync.', delete_after=30)

    @bot.command()
    @commands.is_owner()
    async def latte_prepare_verify(ctx: commands.Context, guilds: Literal['latte', 'support']):
        file = discord.File("assets/latte_verify.png", filename='latte-verify.png')
        if guilds == 'latte':
            await ctx.send(file=file, view=LatteVerifyView(bot))
        elif guilds == 'support':
            await ctx.send(file=file, view=LatteSupportVerifyView(bot))
        await ctx.message.delete()

    @bot.tree.error
    async def tree_error_handler(interaction: Interaction, error: AppCommandError) -> None:
        """ Handles errors for all application commands associated with this CommandTree."""

        error_global = f"An unknown error occurred, sorry"
        # error = getattr(error, 'original', error)
        if isinstance(error, CommandInvokeError):
            error = error.original
        elif isinstance(error, Union[CommandNotFound, MissingPermissions, BotMissingPermissions]):
            error = error
        elif isinstance(error, CommandOnCooldown):
            print(error.retry_after)
            error = error
        # elif isinstance(error, app_commands.BotMissingPermissions):
        #     error = f"I don't have the permissions to do this."
        elif isinstance(error, Union[CommandSignatureMismatch, CommandNotFound]):
            error = 'Sorry, but this command seems to be unavailable! Please try again later...'
        elif isinstance(error, CheckFailure):
            if "nsfw" in str(error):
                error = f'This command is only available in NSFW channels.'  
            else:
                error = f"You can't use this command."
        else:
            error = error_global
            traceback.print_exception(type(error), error, error.__traceback__)

        if interaction is not None:

            # trackback logger
            log_channel = bot.get_channel(970398611030548510)
            await log_channel.send(f"```py\n{traceback.format_exc()[:1950]}```")

            error_content = f'{bot.get_emoji(965746906028441710)} {str(error)[:1950]}' if len(str(error)) < 100 else error_global
            embed = discord.Embed(description=error_content, color=0xfe676e)
            if interaction.response.is_done():
                return await interaction.followup.send(embed=embed, ephemeral=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
    bot.run(os.getenv('DISCORD_TOKEN_TEST'))