import discord
from discord.ext import commands
from difflib import get_close_matches

from ._base import EventsBase

class Error_handler(EventsBase):
      
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            command_names = [str(x) for x in ctx.bot.commands]
            matches = get_close_matches(ctx.invoked_with, command_names)
            if matches:
                matches = "\n".join(matches)
                cm_error = f"I couldn't find that command. Did you mean...\n`{matches}`"
            else:
                return
        elif isinstance(error, commands.UserInputError):
            cm_error = f"{error}"
        elif isinstance(error, commands.DisabledCommand):
            cm_error = f"Command is disabled"
        elif isinstance(error, commands.CommandOnCooldown):
            cm_error = f"You are on cooldown, try again in {error.retry_after:.0f} seconds"
        elif isinstance(error, commands.MessageNotFound):
            cm_error = "I can't find that message!"
        elif isinstance(error, commands.MemberNotFound) or isinstance(error, commands.UserNotFound):
            cm_error = "I can't find that user!"
        elif isinstance(error, commands.ChannelNotFound):
            cm_error = "I can't find that channel!"
        elif isinstance(error, commands.ChannelNotReadable):
            cm_error = "I don't have acces to read anything in that channel!"
        elif isinstance(error, commands.RoleNotFound):
            cm_error = "I can't find that role!"
        elif isinstance(error, commands.EmojiNotFound):
            cm_error = "I can't find that emoji!"
        elif isinstance(error, commands.MissingPermissions):
            cm_error = f"You don't have **{str(error)[15:-35]}** **permission(s)** to run this command!"
        elif isinstance(error, commands.MissingRole):
            cm_error = f"You don't have **{error.missing_role}** role(s) to run this command!"
        elif isinstance(error, commands.MissingAnyRole):
            cm_error = f"You don't have **{error.missing_role}** role(s) to run this command!"
        elif isinstance(error, commands.MissingRequiredArgument):
            cm_error = f"You didn't pass a required argument!"
        elif isinstance(error, commands.NSFWChannelRequired):
            cm_error = f"This channel isn't NSFW"
        elif isinstance(error, commands.CheckFailure):
            cm_error = f"You can't use this command."
            # cm_error = f"I couldn't find that command."
        elif isinstance(error, commands.DisabledCommand):
            cm_error = f"This command is restricted to slash commands." 
        else:
            cm_error = f"An unknown error occurred, sorry"
            print(error)

        embed = discord.Embed(
            description = f"{self.bot.get_emoji(965746906028441710)} {cm_error}",
            color=0xfe676e
        )
        await ctx.send(embed=embed, delete_after=30, ephemeral=True)