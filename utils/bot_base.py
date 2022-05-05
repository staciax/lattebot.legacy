import aiohttp
import asyncpg
import contextlib
import discord
import logging
import traceback
import sys
import os
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from typing import Optional, Union
from dotenv import load_dotenv

# Local
from utils.latte_guild import *
from utils.formats import count_python
from utils.context_managers import UserLock
from utils.useful import LatteContext
from utils.utils import Banner
from utils.latte_guild import LatteSupportVerifyView, LatteVerifyView

from ext.valorant.db import ValorantDB

load_dotenv()

class Latte_Bot(commands.AutoShardedBot):
    
    log = logging.getLogger('Latte_bot.logging')
    log_ext = logging.getLogger('Latte_bot.extensions')
    
    def __init__(self) -> None:
        
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True) #.none()
        intents = discord.Intents.default()
        
        intents.message_content = True
        # intents.members = True
        # intents.presences = True

        super().__init__(
            command_prefix=os.getenv('PREFIX'),
            help_command=None,
            case_insensitive=True,
            allowed_mentions=allowed_mentions,
            intents=intents
        )

        self.initial_extensions = [
            'cogs.jishaku'
        ]

        self.ext_extensions = [
            # 'cogs.testing',
            'cogs.valorant',
            'cogs.anime',
            'cogs.events',
            'cogs.admin',
            'cogs.fun',
            'cogs.misc',
            # 'cogs.music',
            'cogs.infomation',
            'cogs.moderator',
            'cogs.help',
            'cogs.utility'
        ]
       
        self.client_id = 894156599906689095
        self.tester = None
        self.dev_mode = False
        self.help_command = None
        self.owner_id = 240059262297047041
        self.theme = 0xffffff

        # bot cache stuff
        self.bot_version = '0.0.1a'
        self.last_update = [2022, 3, 15]
        self.launch_time = f'<t:{round(datetime.now().timestamp())}:R>'
        self.latte_activity = 'nyanpasu ♡ ₊˚'
        self.line_count = count_python('.')
        
        # guild cache stuff
        self.latte_guild_id = 840379510704046151
        self.latte_sup_guild_id = 887274968012955679
        self.latte_admin_guild_id = 965942839563386910
        self.latte_supprt_url = 'https://discord.gg/n2JZWv7PpK'

        self.invite_url = discord.utils.oauth_url(self.client_id, permissions=discord.Permissions(1101273620486))

        # cache stuff
        self.blacklist = {}
        self.afk_user = {}
        self.user_lock = {}
        self.sleeped_users = {}

        # verify_view_stuff
        self.latte_verify_view = False
        self.latte_support_view = False

        # valorant ext cache stuff
        self.valorant_users = {}
        self.valorant_notify = {}
        
        # self.global_mapping = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.user)
        # Bot based stuff
    
    async def on_ready(self) -> None:   
           
        # await self.http.bulk_upsert_global_commands(self.application_id, [])
        # await self.http.bulk_upsert_guild_commands(self.application_id, 840379510704046151, [])

        if not self.latte_verify_view:
            self.add_view(LatteVerifyView(self))
            self.latte_verify_view = True

        if not self.latte_support_view:
            self.add_view(LatteSupportVerifyView(self))
            self.latte_support_view = True

        await self.tree.sync()
        await self.tree.sync(guild=discord.Object(id=965942839563386910))

        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=self.latte_activity))

        self.log.info(
            f"\n\nLogged in as: {self.user}"
            f"\nActivity: {self.latte_activity}"
            f"\nServers: {len(self.guilds)}"
            f"\nUsers: {sum(g.member_count for g in self.guilds)}"
        )
        
        await self.blacklist_user()

    # @property
    # def stacia(self) -> Optional[discord.User]:
    #     """Returns discord.User of the owner"""
    #     return self.get_user(self.owner_id)
    
    @property
    async def stacia(self) -> Optional[discord.User]:
        """Returns discord.User of the owner"""
        return await self.fetch_user(self.owner_id)

    @property
    def latte(self) -> Optional[discord.Guild]:
        """Returns discord.Guild of the latte guild"""
        return self.get_guild(self.latte_guild_id)
    
    @property
    def latte_support(self) -> Optional[discord.Guild]:
        """Returns discord.Guild of the latte support guild"""
        return self.get_guild(self.latte_sup_guild_id)
    
    @property
    def latte_admin(self) -> Optional[discord.Guild]:
        """Returns discord.Guild of the owner guild"""
        return self.get_guild(self.latte_admin_guild_id)

    async def get_context(self, message: discord.Message, *, cls: Optional[commands.Context] = LatteContext) -> Union[LatteContext, commands.Context]:
        """Override get_context to use a custom Context"""
        return await super().get_context(message, cls=cls)

    #thank_stella_bot
    def get_command_signature(self, command_name: Union[app_commands.Command, app_commands.ContextMenu, str]) -> Optional[str]:
        if isinstance(command_name, str):
            if not (command := self.get_command(command_name)):
                raise Exception("Command does not exist for signature.")
        else:
            command = command_name
        return command

    def add_user_lock(self, lock: UserLock) -> None:
        self.user_lock.update({lock.user.id: lock})

    async def check_user_lock(self, user: Union[discord.Member, discord.User]) -> None:
        if lock := self.user_lock.get(user.id):
            if not lock.locked():
                if isinstance(lock, UserLock):
                    raise lock.error
                raise RuntimeError("You can't invoke another command while another command is running.")
            else:
                self.user_lock.pop(user.id, None)

    async def load_cogs(self) -> None:
        for ext in self.initial_extensions:
            with contextlib.suppress(Exception):
                await self.load_extension(ext)

        for ext in self.ext_extensions:
            with contextlib.suppress(Exception):
                await self.load_extension(ext)
  
    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()        
        self.db: asyncpg.Pool = await self.create_db_pool()
        self.vlr_db = ValorantDB(self.db, os.getenv('CRYPTOGRAPHY_KEY'))
        await self.load_cogs()
        
    async def close(self) -> None:
        await self.db.close()
        await self.session.close()

    async def create_db_pool(self) -> asyncpg.Pool:
        credentials = {
            "user": f"{os.getenv('PSQL_USER')}",
            "password": f"{os.getenv('PSQL_PASSWORD')}",
            "database": f"{os.getenv('PSQL_DB')}",
            "host": f"{os.getenv('PSQL_HOST')}",
            "port": f"{os.getenv('PSQL_PORT')}",
            "min_size": 1,
            "max_size": 5
        }
        localhost = {
            "user": "postgres",
            "password": "RENLYX9",
            "database": "postgres",
            "host": "localhost",
            "port": "5432"
        }
        db = None
        try:
            db = await asyncpg.create_pool(**credentials)
        except Exception as e:
            print(e)
            self.log.error(f"Failed to create database pool.")
        else:
            self.log.info(f"Database pool created.")
        finally:
            self.dispatch('pool_create')
            return db

    async def blacklist_user(self) -> None:
        # await self.wait_until_ready()
        try:
            values = await self.db.fetch('SELECT snowflake_id FROM config.blacklist;')
        except AttributeError:
            pass
        else:
            for value in values:
                self.blacklist[value['snowflake_id']] = True

            self.dispatch('cache_ready')

    async def add_blacklist(self, snowflake_id: int, reason: str) -> None:
        timed = datetime.utcnow()
        values = (snowflake_id, reason, timed)
        await self.db.execute("INSERT INTO config.blacklist VALUES($1, $2, $3)", *values)
        
        self.blacklist[snowflake_id] = True

    async def remove_blacklist(self, snowflake_id: int) -> None:
        await self.db.execute("DELETE FROM config.blacklist WHERE snowflake_id=$1", snowflake_id)
        
        self.blacklist.pop(snowflake_id, None)

    # # ext valorant stuff
    # async def db_valorant(self) -> None:
    #     try:
    #         values = await self.db.fetch('SELECT * FROM valorant.users;')
    #     except AttributeError:
    #         pass
    #     else:
    #         for value in values:
    #             self.valorant_users[value['user_id']] = dict(value)

    #         print(self.valorant_users)
    #         self.dispatch('valorant_cache_ready')

    # async def add_valorant_users(self, user_id: int, data) -> None:        
    #     self.blacklist[user_id] = data

    # async def remove_valorant_users(self, user_id: int) -> None:     
    #     self.valorant_users.pop(user_id, None) 

    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:

        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                print(f'{original.__class__.__name__}: {original}', file=sys.stderr)
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(error)

    async def fetch_banner(self, user: Union[discord.Member, discord.User], *, format: Optional[str] = None, size: Optional[int] = 1024) -> Banner:
        user_id: int = user.id
        usr: dict = await self.http.get_user(user_id) # Call the API to get banner hash.
        state = user._state # The sole reason for this is only for the Asset.
        
        banner_hash: Optional[str] = usr.get('banner') # Tries to get banner hash
        banner_color: Optional[int] = usr.get('accent_color') # Tries to get banner colour

        url = None
        if banner_hash:
            def get_format(): # Tries to get the banner format
                if banner_hash.startswith('a_'): # Check if the banner is animated
                    return 'gif' # Returns the format as gif.
                    
                return (format or 'png') # Returns format arg or png.

            fmt = get_format() # Get the format

            url = f'/banners/{user_id}/{banner_hash}.{fmt}?size={size}' # Generate the URL.

        return Banner(usr, state, url, banner_color) # Return our custom Banner class.

    async def load_extension(self, name: str, *, package: Optional[str] = None) -> None:
        try:
            await super().load_extension(name, package=package)
            self.log_ext.info(f'Loaded extension {name}')
        except Exception as e:
            self.log_ext.error(f'Failed to load extension {name}', exc_info=e)
            raise e
    
    async def unload_extension(self, name: str, *, package: Optional[str] = None) -> None:
        try:
            await super().unload_extension(name, package=package)
            self.log_ext.info(f'Unloaded extension {name}')
        except Exception as e:
            self.log_ext.error(f'Failed to unload extension {name}', exc_info=e)
            raise e
    
    async def reload_extension(self, name: str, *, package: Optional[str] = None) -> None:
        try:
            await super().reload_extension(name, package=package)
            self.log_ext.info(f'Reloaded extension {name}')
        except Exception as e:
            self.log_ext.error(f'Failed to reload extension {name}', exc_info=e)
            raise e