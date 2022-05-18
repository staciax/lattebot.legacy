import discord
import os
from discord import app_commands, Interaction, Member, User
from discord.ext import commands, menus
from typing import Optional, Union, Dict, List, Literal

from utils import Cog
from utils.formats import format_dt
from utils.emojis import LATTE_EMOJI 
from utils.checks import owner_only
from utils.menus import LattePage, SimplePageSource
from utils.latte_guild import LatteSupportVerifyView, LatteVerifyView

latte_admin_guild_id = 965942839563386910
latte_admin_guild = discord.Object(id=latte_admin_guild_id)

class BlackListPages(LattePage):
    def __init__(self, entries, *, interaction: discord.Interaction, per_page: int = 12, ephemeral: bool = False):
        super().__init__(SimplePageSource(entries, per_page=per_page), interaction=interaction, ephemeral=ephemeral, compact=True)
        self.embed = discord.Embed(color=0xffffff)

class Admin(Cog):
    '''Admin commands'''

    @commands.Cog.listener('on_ready')
    async def sync_appcommands(self):
        await self.bot.tree.sync(guild=latte_admin_guild)

    @property
    def display_emoji(self) -> discord.Emoji:
        return LATTE_EMOJI.MOLANG_COFFEE
        # return self.bot.get_emoji(840678426867793921)

    # async def cog_check(self, ctx: LatteContext) -> bool:
    #     return await commands.is_owner().predicate(ctx) # type: ignore

    blacklist = app_commands.Group(name='blacklist', description='Blacklist commands', guild_ids=[latte_admin_guild_id])

    @blacklist.command(name='add', description='Blacklist a user or guild')
    @app_commands.describe(user='The user to blacklist', reason='The reason for blacklisting the user')
    @owner_only()
    async def blaclist_add(self, interaction: Interaction, user: Union[Member, User], reason: str):
        await self.bot.add_blacklist(user.id, reason)
        embed = discord.Embed(description=f"**{user}** are now blacklisted.")
        await interaction.response.send_message(embed=embed)
    
    @blacklist.command(name='remove', description='Remove a user or guild from the blacklist')
    @app_commands.describe(user='The user to remove blacklist')
    @owner_only()
    async def blaclist_remove(self, interaction: Interaction, user: Union[Member, User]):
        await self.bot.remove_blacklist(user.id)
        embed = discord.Embed(description=f"**{user}** are no longer blacklisted.")
        await interaction.response.send_message(embed=embed)

    @blacklist.command(name='check', description='Check if a user or guild is blacklisted')
    @app_commands.describe(user='The user to check blacklist')
    @owner_only()
    async def blacklist_check(self, interaction: Interaction, user: Union[Member, User]):

        query = "SELECT * FROM config.blacklist"

        if user is None:
            data = await self.db.fetch(query)
        else:
            if data := await self.bot.db.fetchrow(query + " WHERE snowflake_id=$1", user.id):
                reason = data["reason"]
                embed = discord.Embed(title=f"**{user}** is blacklisted",description=f"Reason: ```{reason}```")
                embed.add_field(name="Time of blacklist", value=format_dt(data["timestamp"], 'R'))
                await interaction.response.send_message(embed=embed)
            else:
                raise RuntimeError(f"**{user}** is not blacklisted")

    @blacklist.command(name='list', description='List all blacklisted users')
    @owner_only()
    async def blacklist_check(self, interaction: Interaction):
        query = "SELECT * FROM config.blacklist"
        blacklist = await self.db.fetch(query)

        blacklist_users = []
        if blacklist or len(blacklist) != 0:
            for data in blacklist:
                snowflake_id = data["snowflake_id"]
                user = self.bot.get_user(snowflake_id) or await self.bot.fetch_user(snowflake_id)
                blacklist_users.append(f"{user} | `{user.id}`")

            p = BlackListPages(blacklist_users, interaction=interaction)
            return await p.start() 
            
        raise RuntimeError("No blacklisted users.")

    @app_commands.command()
    @app_commands.describe(extension='extension name')
    @app_commands.guilds(latte_admin_guild)
    @owner_only()
    async def load(self, interaction: Interaction, extension: str):
        """Loads an extension."""

        try:
            await self.bot.load_extension(f'{extension}')
        except commands.ExtensionAlreadyLoaded:
            raise commands.UserInputError(f"The extension is already loaded.")
        except Exception as e:
            print(e)
            raise commands.UserInputError('The extension load failed')
        else:
            embed = discord.Embed(description= f"{LATTE_EMOJI.GREENTICK} Load : `{extension}`", color = 0x8be28b)
            await interaction.response.send_message(embed=embed)
                   
    @app_commands.command()
    @app_commands.describe(extension='extension name')
    @app_commands.guilds(latte_admin_guild)
    @owner_only()
    async def unload(self, interaction: Interaction, extension: str):
        """Unloads an extension."""

        try:
            await self.bot.unload_extension(f'{extension}')
        except commands.ExtensionNotLoaded:
            raise commands.UserInputError(f'The extension was not loaded.')
        except Exception as e:
            print(e)
            raise commands.UserInputError('The extension unload failed')
        else:
            embed = discord.Embed(description= f"{LATTE_EMOJI.GREENTICK} Unload : `{extension}`", color = 0x8be28b)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name='reload')
    @app_commands.describe(extension='extension name')
    @app_commands.guilds(latte_admin_guild)
    @owner_only()
    async def reload_(self, interaction: Interaction, extension: str):
        """Reloads an extension."""

        try:
            print(f"Reloading {extension}")
            await self.bot.reload_extension(f'{extension}')
        except commands.ExtensionNotLoaded:
            raise RuntimeError(f'The extension was not loaded.')
        except commands.ExtensionNotFound:
            raise RuntimeError(f'The Extension Not Found')
        except Exception as e:
            print(e)
            raise RuntimeError('The extension reload failed')
        else:
            embed = discord.Embed(description= f"{LATTE_EMOJI.GREENTICK} Reload : `{extension}`", color = 0x8be28b)
            await interaction.response.send_message(embed=embed)
        
    @load.autocomplete('extension')
    @unload.autocomplete('extension')
    @reload_.autocomplete('extension')
    async def tags_autocomplete(self, interaction: Interaction, current: str) -> List[app_commands.Choice[str]]:
        
        extensions = []
        extensions.extend(self.bot.initial_extensions)
        extensions.extend(self.bot.ext_extensions)

        if interaction.user.id != self.bot.owner_id:
            return [app_commands.Choice(name='Only owner can use this command', value='Owner only can use this command')]
            
        cogs = [ext.lower() for ext in extensions]
        return [app_commands.Choice(name=cog.split('.')[1], value=cog) for cog in cogs]
        
    # @app_commands.command()
    # async def toggle(self, interaction: Interaction, command: str):
    #     command = self.bot.get_command(command)
    #     command.enabled = not command.enabled
    #     ternary = "Enabled" if command.enabled else "disabled"
    #     toggle_color = 0x8be28b if command.enabled else 0xFF7878
    #     embed = discord.Embed(color=toggle_color)
    #     embed.description = f"Successfully {ternary} the `{command.name}` command."
    #     await ctx.maybe_reply(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, sync_type: str):
        
        ctx.typing()
        try:
            if sync_type == 'guild':
                guild = discord.Object(id=ctx.guild.id)
                self.bot.tree.copy_global_to(guild=guild)
                await self.bot.tree.sync(guild=guild)
                await ctx.reply(f"Synced guild !")
            elif sync_type == 'global':
                await self.bot.tree.sync()
                await ctx.reply(f"Synced global !")
        except discord.Forbidden:
            await ctx.send("Bot don't have permission to sync. : https://cdn.discordapp.com/attachments/939097458288496682/950613059150417970/IMG_3279.png")
        except discord.HTTPException:
            await ctx.send('Failed to sync.', delete_after=30)
    
    @commands.command()
    @commands.is_owner()
    async def unsync(self, ctx: commands.Context, sync_type: str):

        if self.bot.owner_id is None:
            if ctx.author.guild_permissions.administrator != True:
                await ctx.reply("You don't have **Administrator permission(s)** to run this command!", delete_after=30)
                return

        ctx.typing()
        try:
            if sync_type == 'guild':
                guild = discord.Object(id=ctx.guild.id)
                commands = self.bot.tree.get_commands(guild=guild)
                for command in commands:
                    self.bot.tree.remove_command(command, guild=guild)
                await self.bot.tree.sync(guild=guild)
                await ctx.reply(f"Un-Synced guild !")    
            elif sync_type == 'global':
                commands = self.bot.tree.get_commands()
                for command in commands:
                    self.bot.tree.remove_command(command)
                await self.bot.tree.sync()
                await ctx.reply(f"Un-Synced global !")
        except discord.Forbidden:
            await ctx.send("Bot don't have permission to unsync. : https://cdn.discordapp.com/attachments/939097458288496682/950613059150417970/IMG_3279.png")
        except discord.HTTPException:
            await ctx.send('Failed to unsync.', delete_after=30)

    @commands.command()
    @commands.is_owner()
    async def latte_prepare_verify(self, ctx: commands.Context, guilds: Literal['latte', 'support']):
        file = discord.File("assets/latte_verify.png", filename='latte-verify.png')
        if guilds == 'latte':
            await ctx.send(file=file, view=LatteVerifyView(self.bot))
        elif guilds == 'support':
            await ctx.send(file=file, view=LatteSupportVerifyView(self.bot))
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Admin(bot))