import asyncio
import discord
import random
import contextlib
from discord.ext import commands, tasks
from discord import app_commands, Interaction, Forbidden, HTTPException
from discord.utils import MISSING
from typing import Literal, Optional, Union, Any, Tuple, List, Dict

from datetime import datetime, time
from utils.bot_base import Latte_Bot
from utils.emojis import LATTE_EMOJI
from utils.checks import owner_only, cooldown_for_everyone_but_me
from ext.valorant.locale import LocaleResponse, InteractionLanguage

# valorant extension
from ext.valorant import *

class Notifys(commands.Cog):

    def __init__(self, bot: Latte_Bot) -> None:
        self.bot = bot
        self.db = bot.vlr_db
        self.notifys.start()

    @property
    def display_emoji(self) -> discord.Emoji:
        return str(LATTE_EMOJI.MOLANG_COFFEE)
        # return self.bot.get_emoji(840678426867793921)

    def cog_unload(self) -> None:
        self.notifys.cancel()

    async def get_endpoint(self, user_id: int) -> VALORANT_ENDPOINT:
        data = await self.db.is_data(user_id)
        endpoint = VALORANT_ENDPOINT()
        endpoint.activate(data)
        return endpoint

    async def send_notify(self):
        notify_users = await self.db._get_all_notify_users()  # fetch  1

        for user in notify_users:
            try:
                user_id = int(user['user_id'])
                endpoint = await self.get_endpoint(user_id)
                offer = endpoint.store_fetch_storefront()
                author = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                skin_list = GetFormat.offer_format(offer, language = 'en-US')

                if user['notify_mode'] == 'All':
                    embeds = Generate_Embed.notify_all(endpoint.player, skin_list)
                    await author.send(embeds=embeds)

                elif user['notify_mode'] == 'Spc':
                    data_spc = await self.db._get_notify_ByUserID(user_id)
                    await Generate_Embed.notify_specified(data_spc, skin_list, author, self.bot.db)

            except Exception as e:
                print('send_notify', e)

    @tasks.loop(time=time(hour=0, minute=0, second=10)) #utc 00:00:15
    # @tasks.loop(seconds=10)  # utc 00:00:15
    async def notifys(self) -> None:
        __verify_time = datetime.utcnow()
        if __verify_time.hour == 0 and __verify_time.minute <= 10:
            await self.send_notify()

    @notifys.before_loop
    async def before_daily_send(self) -> None:
        await self.bot.wait_until_ready()
        print('Checking new store skins for notifys...')

    # @notifys.error
    # async def notifys_error(self, error) -> None:
    #     print(f"An error ocurred in notify during run number {self.notifys.current_loop}")
    #     traceback.print_exc()
    #     self.notifys.restart()

    notify = app_commands.Group(name='notify', description='Notify commands')

    @notify.command(name='add', description='Set a notification when a specific skin is available on your store')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    @app_commands.describe(skin='The name of the skin you want to notify')
    async def notify_add(self, interaction: Interaction, skin: str) -> None:
        """Set a notification when a specific skin is available on your store"""

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)
        language = 'en-US'

        db = self.bot.db
        user_id = interaction.user.id
        guild_id = interaction.guild_id
        await self.db.is_login(user_id)

        user_notify = await self.db.get_notify_user(user_id)

        if len(user_notify) > 20:
            raise RuntimeError('You have reached the maximum amount of notifications')
        #     raise RuntimeError(response.get('notify_limit'))

        uuid = skin
        skin = GetItem.get_skin(uuid)
        emoji = get_emoji_tier(uuid)
        name = skin['names'][language]
        icon = skin['icon']
        uuid = skin['uuid']

        if uuid in [x['uuid'] for x in user_notify]:
            raise RuntimeError(f'{emoji} **{name}** is already in your notifys')

        await self.db.notify_skin_check(user_id, uuid, emoji, name)
        await self.db.notify_insert(user_id, uuid, guild_id)
        await self.db.notify_status(user_id)
        
        embed = Embed(f'Successfully set an notify for the {emoji} **{name}**')
        embed.set_thumbnail(url=icon)

        view = Notify(user_id, uuid, name, db)

        await interaction.response.send_message(embed=embed, view=view)

    @notify_add.autocomplete('skin')
    async def notify_add_autocomplete(self, interaction: Interaction, current: str) -> List[app_commands.Choice[str]]:
  
        await interaction.response.defer()

        cache = JSON.read('cache')

        default_language = 'en-US'

        choice_list = {}

        namespace = interaction.namespace.skin
        namespace_split = str(namespace).lower().split()

        for skin in cache['skins'].values():
            if skin['levelone']:
                name: str = skin['names'][default_language]
                name_split = name.split()
                with contextlib.suppress(IndexError):
                    if name.lower().startswith(tuple(namespace_split)):
                        if len(namespace_split) > 1:
                            for item in name_split:
                                if item.lower().startswith(namespace_split[1]) and name.lower() != item.lower():
                                    choice_list[name] = skin['uuid']
                        else:
                            choice_list[name] = skin['uuid']

        if not choice_list:
            popular_skin =(
            'prime', 'reaver', 'glitchpop', 'rgx', 'spectrum', 'magepunk',
            'recon', 'sovereign', 'sentinels', 'blastx', 'ion', 'oni'
        )
            popular_skin_shuffle = tuple(random.sample(popular_skin, len(popular_skin)))
            return [app_commands.Choice(name=skin['names'][default_language], value=skin['uuid']) for skin in sorted(cache['skins'].values(), key=lambda x: x['names'][default_language]) \
                if skin['names'][default_language].lower().startswith(popular_skin_shuffle[:2]) and skin['levelone']
            ][:10]

        return [app_commands.Choice(name=name_x, value=uuid) for name_x, uuid in sorted(choice_list.items(), key=lambda x: x[0])][:12]

    @notify.command(name='list', description='View skins you have set a for notification.')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def notify_list(self, interaction: Interaction) -> None:
        """View skins you have set a notification for"""

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        user_id = interaction.user.id
        await self.db.is_login(user_id)

        db = self.bot.db
        view = Notify_list(interaction, db, language)
        await view.start()
    
    @notify.command(name='mode', description='Change notification mode')
    @app_commands.describe(mode='Choose notification')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def notify_mode(self, interaction: Interaction, mode: Literal['Specified Skin', 'All Skin', 'Off']) -> None:
        """Set Skin Notifications mode"""

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)
        
        user_id = interaction.user.id
        # channel_id = interaction.channel.id
        data = await self.db.is_data(user_id)
        db = self.bot.db

        notify = {'Specified Skin': 'Spc', 'All Skin': 'All', 'Off': 'Off'}
        change = notify[mode]

        embed = Embed(f"Successfully set notify mode to **{mode}**")
        if mode == 'Specified Skin': embed.set_image(url=f"https://i.imgur.com/RF6fHRY.png")
        elif mode == 'All Skin': embed.set_image(url=f"https://i.imgur.com/Gedqlzc.png")

        query = 'UPDATE valorant.users SET notify_mode=$1 WHERE user_id = $2;'
        await db.execute(query, change, user_id)
            
        return await interaction.response.send_message(embed=embed)

    @notify.command(name='test', description='Testing notification')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def notify_test(self, interaction: Interaction) -> None:

        await interaction.response.defer(ephemeral=True)
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)
        response_test = LocaleResponse('notify_test', interaction.locale)

        user_id = interaction.user.id
        data = self.db.is_login(user_id)

        try:
            endpoint = await self.get_endpoint(user_id)
            offer = endpoint.store_fetch_storefront()
            author = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            skin_list = GetFormat.offer_format(offer, language = 'en-US')

            if data['notify_mode'] == 'All':
                embeds = Generate_Embed.notify_all(endpoint.player, skin_list)
                await author.send(embeds=embeds)

            elif data['notify_mode'] == 'Spc':
                data_spc = await self.db._get_notify_ByUserID(user_id)
                await Generate_Embed.notify_specified(data_spc, skin_list, author, self.bot.db)
        except Forbidden:
            raise RuntimeError(response_test.get('BOT_MISSING_PERM'))
        except HTTPException:
            raise RuntimeError(response_test.get('FAILED_SEND_NOTIFY'))
        except Exception as e:
            print('notify_test', e)
            raise RuntimeError(f"{response_test.get('FAILED_SEND_NOTIFY')} - {e}")
        else:
            await interaction.followup.send(embed=Embed(response_test.get('NOTIFY_IS_WORKING'), color=0x77dd77), ephemeral=True)

class ValorantCommands(commands.Cog, name='Valorant'):
    """Valorant API Commands"""

    def __init__(self, bot: Latte_Bot) -> None:
        self.bot = bot
        self.db = bot.vlr_db

    @property
    def display_emoji(self) -> discord.Emoji:
        return str(LATTE_EMOJI.VALORANT)
        # return self.bot.get_emoji(955743009138429962)

    @commands.Cog.listener('on_guild_remove')
    async def remove_guild(self, guild: discord.Guild):
        await self.db.delete_guild(guild.id)

    def authenticate(self, username: str, password: str, locale_code: str) -> VALORANT_ENDPOINT:
        auth = Auth()
        auth.locale_code = locale_code
        data = auth.authenticate(username, password)
        return data

    async def get_endpoint(self, user_id: int, locale_code: str, username:str = None, password: str= None) -> VALORANT_ENDPOINT:
        
        if username is not None and password is not None:
            auth = self.db.auth
            auth.local_code = locale_code
            data = auth.temp_auth(username, password)
        elif username or password:
            raise RuntimeError(f"Please provide both username and password!")
        else:
            data = await self.db.is_data(user_id, locale_code)

        data['locale_code'] = locale_code
        endpoint = VALORANT_ENDPOINT()
        endpoint.activate(data)
        return endpoint

    @app_commands.command()
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    @app_commands.describe(username='Input username', password='Input password')
    async def login(self, interaction: Interaction, username: str, password: str) -> None:
        """Log in with your Riot accounts"""

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        user_id = interaction.user.id
        row = await self.db.is_login(user_id, True)
        is_update = True if row else False

        auth = self.authenticate(username, password, interaction.locale)

        if auth['auth'] == 'response':
            await interaction.response.defer(ephemeral=True)

            login = await self.db.login(user_id, auth, interaction.guild_id, interaction.locale, is_update)

            if login['auth']:
                embed = Embed(description=f"{response.get('SUCCESS')} **{login['player']}**")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            elif not login['auth']:
                raise RuntimeError(f"{response.get('FAILED')}")
    
            raise RuntimeError(f"{response.get('FAILED')}")

        elif auth['auth'] == '2fa':
            modal = TwoFA_UI(interaction, self.db, auth, is_update, response)
            await interaction.response.send_modal(modal)

    @app_commands.command()
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def logout(self, interaction: Interaction) -> None:
        """Logout and Delete your accounts from database"""

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        user_id = interaction.user.id
        await self.db.logout(user_id, interaction.locale)

        embed = Embed(response.get('SUCCESS'))
        await interaction.response.send_message(embed=embed, ephemeral=True)

        user_notify = await self.db.get_notify_user(user_id)

        if len(user_notify) != 0:
            view = Confirm(interaction)
            is_notify = response.get('IS_NOTIFY')
            remove_notify = response.get('REMOVE_NOTIFY')

            view.message = await interaction.followup.send(is_notify.format(amount=len(user_notify)), ephemeral=True, view=view)
            await view.wait()
            if view.value is None:
                return await view.message.edit(view=None)
            elif view.value:
                await self.db.delete_user_notify(user_id)
                return await view.message.edit(content=remove_notify, view=None)
    
            await view.message.edit(content=f'\u200b', view=None)

    @app_commands.command()
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    @app_commands.describe(username='Input username (without login)', password='password (without login)')
    async def store(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        """Shows your daily store in your accounts"""

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False
        await interaction.response.defer(ephemeral=is_private_message)

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)
        
        offer = endpoint.store_fetch_storefront()
        embeds = Generate_Embed.store(endpoint.player, offer, language, response)

        await interaction.followup.send(embeds=embeds, view=share_button(interaction, embeds) if is_private_message else MISSING)
        
    @app_commands.command()
    @app_commands.describe(username='Input username (without login)', password='password (without login)')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def battlepass(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        """View your battlepass current tier"""

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False

        await interaction.response.defer(ephemeral=is_private_message)

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)
        
        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)

        data = endpoint.fetch_contracts()
        content = endpoint.fetch_content()
        season = get_season_by_content(content)
        embed = Generate_Embed.battlepass(endpoint.player, data, season, language, response)

        await interaction.followup.send(embed=embed, view=share_button(interaction, [embed]) if is_private_message else MISSING)

    @app_commands.command()
    @app_commands.describe(username='Input username (without login)', password='password (without login)')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def point(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        """View your remaining Valorant and Riot Points (VP/RP)"""

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False
    
        await interaction.response.defer(ephemeral=is_private_message)

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)

        data = endpoint.store_fetch_wallet()
        embed = Generate_Embed.point(endpoint.player, data, language, response)

        await interaction.followup.send(embed=embed, view=share_button(interaction, [embed]) if is_private_message else MISSING)

    @app_commands.command()
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    @app_commands.describe(username='Input username (without login)', password='password (without login)')
    async def mission(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        """View your daily/weekly mission progress"""

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False
        await interaction.response.defer(ephemeral=is_private_message)

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)

        data = endpoint.fetch_contracts()

        embed = Generate_Embed.mission(endpoint.player, data, language, response)

        await interaction.followup.send(embed=embed, view=share_button(interaction, [embed]) if is_private_message else MISSING)

    @app_commands.command()
    @app_commands.describe(cookie='Your cookies')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def cookies(self, interaction: Interaction, cookie: str) -> None:
        """Log in with your Riot acoount by Cookies"""

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        await interaction.response.defer()
        response = await self.db.cookie_login(interaction.user.id, cookie, interaction.guild_id, interaction.locale)

        if response['auth']:
            embed = Embed(f"Successfully logged in as **{response['player']}!**")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        elif not response['auth']:
            raise RuntimeError(f"{response['error']}")
        
        raise RuntimeError(f"2FA Code is valid")

    @app_commands.command(name='nightmarket')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    @app_commands.describe(username='Input username (without login)', password='password (without login)')
    async def nightmarket(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        """Show skin offers on the nightmarket"""

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False
        await interaction.response.defer(ephemeral=is_private_message)

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)
        
        offer = endpoint.store_fetch_storefront()
        embeds = Generate_Embed.nightmarket(endpoint.player, offer, language, response)

        await interaction.followup.send(embeds=embeds, view=share_button(interaction, embeds) if is_private_message else MISSING)

    # inspired by https://github.com/giorgi-o
    @app_commands.command(description="inspect a specific bundle")
    @app_commands.describe(bundle="The name of the bundle you want to inspect!")
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def bundle(self, interaction: Interaction, bundle: str) -> None:
        
        await interaction.response.defer()

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        # cache
        cache = JSON.read('cache')
        bundle_data = cache['bundles']

        finded_bundle = bundle_data.get(bundle, None)
        if finded_bundle is None:
            raise RuntimeError(response.get('NOT_FOUND_BUNDLE'))

        # bundle view
        view = BaseBundle(interaction, finded_bundle, response, language)
        await view.start()

    @bundle.autocomplete('bundle')
    async def bundle_autocomplete(self, interaction: Interaction, current: str) -> List[app_commands.Choice[str]]:
        """Autocomplete for bundle"""
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)
        
        # default language language
        default_language = 'en-US'

        bundle = interaction.namespace.bundle

        # cache
        cache = JSON.read('cache')

        find_bundle = [cache['bundles'][i] for i in cache['bundles'] \
            if bundle.lower() in cache['bundles'][i]['names'][default_language].lower() or \
                # bundle.lower() in cache['bundles'][i]['names'][language].lower() or \
                    cache['bundles'][i]['names'][default_language].lower().startswith(bundle.lower())
        ]

        return [app_commands.Choice(name=bundle['names'][default_language], value=bundle['uuid'])
            for bundle in sorted(find_bundle, key=lambda x: x['names'][default_language])
        ][:10]
            
    # inspired by https://github.com/giorgi-o
    @app_commands.command(description="Show the current featured bundles")
    async def bundles(self, interaction: Interaction) -> None:

        await interaction.response.defer()
        
        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        # endpoint
        endpoint = await self.get_endpoint(self.bot.owner_id, interaction.locale)

        # data
        bundle_entries = endpoint.store_fetch_storefront()

        # bundle view
        view = BaseBundle(interaction, bundle_entries, response, language)
        await view.start_furture()
    
    valorant = app_commands.Group(name='valorant', description='valorant commands')

    @valorant.command()
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    @app_commands.describe(region='Select region to get the leaderboard')
    async def leaderboard(self, interaction: Interaction, region: Literal['AP', 'EU', 'NA', 'KR']) -> None:
        """Shows your Region Leaderboard"""

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        await interaction.response.defer()

        r = await self.bot.session.get(f'https://api.henrikdev.xyz/valorant/v1/leaderboard/{region.lower()}')
        if r.status != 200: raise RuntimeError(f'Error to fetch leaderboard')
        
        data = await r.json()
        entries = GetFormat.leaderboard(data)

        p = LeaderboardPages(entries=entries, interaction=interaction)
        p.embed.title = f"{region.upper()} Leaderboard"
        await p.start()

    @valorant.command(name='info')
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def _info(self, interaction: Interaction) -> None:
        """Shows your account info"""

        # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        raise RuntimeError('Not available at the moment')
        # ingame status name notify_stutus

    @valorant.command()
    @app_commands.choices(name=[app_commands.Choice(name=name, value=uuid) for name, uuid in AgentID.items()])
    async def agent(self, interaction: Interaction, name: str = None) -> None:
        
        view = AgentInfoView(interaction)
        await view.start(name)
   
    @valorant.command(name='reload')
    @app_commands.rename(reload_type='reload')
    @app_commands.describe(reload_type='Choose the reload type')
    @owner_only()
    async def _reload(self, interaction: Interaction, reload_type: Literal['Skin Price', 'Cache']) -> None:
        """Reload cache for valorant data"""

        await interaction.response.defer(ephemeral=True)

        if reload_type == 'Skin Price':
            endpoint = await self.get_endpoint(interaction.user.id, interaction.locale)
            price = endpoint.store_fetch_offers()
            fetch_price(price)
        elif reload_type == 'Cache':
            get_cache()

        await interaction.followup.send(embed=Embed(f'Reloaded **{reload_type}** complete'))

    @valorant.command(name='clear_database')
    @app_commands.describe(clear_type='Choose the clear type')
    @owner_only()
    async def _clear_db(self, interaction: Interaction, clear_type: Literal['Users', 'Notify']) -> None:
        """Clear database"""

        await interaction.response.defer()

        if clear_type == 'Users':
            await self.bot.db.execute('DELETE FROM valorant.users;')
        elif clear_type == 'Notify':
            await self.bot.db.execute('DELETE FROM valorant.notifys;')
        
        await interaction.followup.send(embed=Embed(f'Successfully cleared database `valorant.{clear_type.lower()}`'))

    @valorant.command()
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def inventory(self, interaction: Interaction) -> None:
        """Shows your inventory"""

        # # language
        language = InteractionLanguage(interaction.locale)
        response = LocaleResponse(interaction.command.name, interaction.locale)

        await interaction.response.defer()

        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale)

        data = endpoint.fetch_player_loadout()

        loadout = GetFormat.inventory(data)
        
        view = InventoryView(interaction, loadout, endpoint, data, language)
        await view.start()

    # ---------- PRIVATE FUNCTIONS ---------- #

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=840379510704046151))
    async def dodge(self, interaction: Interaction, username: str = None, password: str = None) -> None:
        """Valorant: Dodge a match"""

        await interaction.response.defer(ephemeral=True)

        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)
        endpoint.pregame_quit_match()

        await interaction.followup.send('Dogged!', ephemeral=True)

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=840379510704046151))
    @app_commands.choices(agents=[app_commands.Choice(name=name, value=name) for name, uuid in AgentID.items()])
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    @app_commands.describe(agents='Choose the agent')
    async def instalock(self, interaction: Interaction, agents: str, username: str = None, password: str = None) -> None:
        """Valorant: Instalock a agent"""

        import time
        from ext.valorant.resources import agents_emoji

        await interaction.response.defer(ephemeral=True)

        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)

        timeout = 30 # 1 minute
        timeout_start = time.time()
    
        match = None
        while time.time() < timeout_start + timeout:
            try:
                match = endpoint.pregame_fetch_player()
            except PhaseError:
                pass
            else:
                if not match:
                    raise RuntimeError('No match found')
                break
            
            await asyncio.sleep(1)
        
        await asyncio.sleep(3)

        agent_id = AgentID.get(agents)
        emoji = agents_emoji[agents]
        match_id = match["MatchID"]
        endpoint.pregame_lock_character(agent_id, match_id)
        
        await interaction.followup.send(f"**Instalock:** {emoji} {agents}")
                
    # @valorant.command()
    # async def rank(self, interaction: Interaction, name:str, tag: str) -> None:
    #     """Shows rank by name and tag"""
        ...
        # # language
        # language = InteractionLanguage(interaction.locale)
        # response = LocaleResponse(interaction.command.name, interaction.locale)

        # endpoint = await self.get_endpoint(self.bot.owner_id, interaction.locale)
        # endpoint.fetch_player_mmr()


        # user_id = interaction.user.id
        # data = await self.db.is_data(user_id)

        # player = data['player_name']

        # api = VALORANT_ENDPOINT(data)
        # api.activate()

        # rank = api.get_player_tier_rank()
        # rank_emoji = ranks[str(rank)]['emoji']
        # rank_name = ranks[str(rank)]['name']

        # return await interaction.response.send_message(f"{player}")

    # @valorant.command()
    # @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    # async def party(self, interaction: Interaction):
    #     endpoint = await self.get_endpoint(interaction.user.id)
    #     from ext.valorant.resources import agents_emoji

    #     class PartyView(discord.ui.View):
    #         def __init__(self, interaction: interaction):
    #             self.interaction = interaction
    #             super().__init__()
    #             self.clear_items()
    #             self.add_item(AgentSelectMenu())

    #     class AgentSelectMenu(discord.ui.Select['PartyView']):
    #         def __init__(self):
    #             super().__init__(
    #                 placeholder='Select a Agent...',
    #                 min_values=1,
    #                 max_values=1,
    #                 row=0,
    #             )
    #             self.__fill_options()

    #         def __fill_options(self) -> None:
    #             for name, uuid in AgentID.items():
    #                 self.add_option(label=name, value=uuid, emoji=agents_emoji[name])

    #         async def callback(self, interaction: discord.Interaction):
    #             assert self.view is not None
    #             value = self.values[0]
    #             endpoint.pregame_select_character(value)

    #     class QeueueSelectMenu(discord.ui.Select['PartyView']):
    #         def __init__(self):
    #             super().__init__(
    #                 placeholder='Select a Agent...',
    #                 min_values=1,
    #                 max_values=1,
    #                 row=0,
    #             )
    #             self.__fill_options()

    #         def __fill_options(self) -> None:
    #             for name, emoji in agents_emoji.items():
    #                 self.add_option(label=name, value=name, emoji=emoji)

    #         async def callback(self, interaction: discord.Interaction):
    #             assert self.view is not None
    #             value = self.values[0]
    #             print(value)
        
    #     print(endpoint.pregame_fetch_match())
                
    #     await interaction.response.send_message('testing', view=PartyView(interaction))
    
    # @app_commands.command()
    # @valorant.command()
    # @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    # @only_latte_guild()
    # async def party(self, interaction: Interaction) -> None:
    #     """ Pick Agent """

    #     await interaction.response.defer()
    #     endpoint = await self.get_endpoint(interaction.user.id)

    #     count = 0

    #     while True:
    #         try:
    #             match = endpoint.pregame_fetch_match()
    #         except Exception as e:
    #             pass
    #         else:
    #             break

    #         if count == 60:
    #             return await interaction.followup.send("timeout")
            
    #         await asyncio.sleep(1)
    #         count += 1

    #     team_id = match['AllyTeam']['TeamID']
    #     color_overite = 0x30efb8 if team_id == 'Blue' else 0xef605a
    #     text_overite = 'กันก่อน' if team_id == 'Blue' else 'บุกก่อน'

    #     AgentID = {
    #         'Astra': '41fb69c1-4189-7b37-f117-bcaf1e96f1bf',
    #         'Breach': '5f8d3a7f-467b-97f3-062c-13acf203c006',
    #         'Brimstone': '9f0d8ba9-4140-b941-57d3-a7ad57c6b417',
    #         'Chamber': '22697a3d-45bf-8dd7-4fec-84a9e28c69d7',
    #         'Cypher': '117ed9e3-49f3-6512-3ccf-0cada7e3823b',
    #         'Fade': 'dade69b4-4f5a-8528-247b-219e5a1facd6',
    #         'Jett': 'add6443a-41bd-e414-f6ad-e58d267f4e95',
    #         'KAY/O': '601dbbe7-43ce-be57-2a40-4abd24953621',
    #         'Killjoy': '1e58de9c-4950-5125-93e9-a0aee9f98746',
    #         'Neon': 'bb2a4828-46eb-8cd1-e765-15848195d751',
    #         'Omen': '8e253930-4c05-31dd-1b6c-968525494517',
    #         'Phoenix': 'eb93336a-449b-9c1b-0a54-a891f7921d69',
    #         'Raze': 'f94c3b30-42be-e959-889c-5aa313dba261',
    #         'Reyna': 'a3bfb853-43b2-7238-a4f1-ad90e9e46bcc',
    #         'Sage': '569fdd95-4d10-43ab-ca70-79becc718b46',
    #         'Skye': '6f2a04ca-43e0-be17-7f36-b3908627744d',
    #         'Sova': '320b2a48-4d9b-a075-30f1-1f93a9b638fa',
    #         'Viper': '707eab51-4836-f488-046a-cda6bf494859',
    #     }

    #     class PartyView(discord.ui.View):
    #         def __init__(self, interaction: interaction):
    #             self.interaction = interaction
    #             super().__init__()
    #             self.clear_items()
    #             self.add_item(AgentSelectMenu())

    #     class AgentSelectMenu(discord.ui.Select['PartyView']):
    #         def __init__(self):
    #             super().__init__(
    #                 placeholder='Select a Agent...',
    #                 min_values=1,
    #                 max_values=1,
    #                 row=0,
    #             )
    #             self.__fill_options()

    #         def __fill_options(self) -> None:
    #             for name, uuid in AgentID.items():
    #                 self.add_option(label=name, value=uuid, emoji=agents_emoji[name])

    #         async def callback(self, interaction: discord.Interaction):
    #             assert self.view is not None
    #             value = self.values[0]
    #             endpoint.pregame_select_character(value)
    #             endpoint.pregame_lock_character(value)
    #             await interaction.response.send_message('select agent', ephemeral=True)

    #     embed = discord.Embed(
    #         description=text_overite,
    #         color=color_overite
    #     )
        
    #     await interaction.followup.send(embed=embed, view=PartyView(interaction))

    # #@valorant.command(name='Account Data')
    # async def account_data(self, name: str, tag: str) -> None:
    #     # /valorant/v1/account/:name/:tag
    #     ...

    # async def mmr_data(self, name: str, tag:str, region: Literal['AP', 'EU', 'NA', 'KR'], api_version: Literal['1','2']) -> None:
    #     # /valorant/:version/mmr/:name/:tag
    #     ...

    # async def mmr_by_puuid(self, puuid: str, region: Literal['AP', 'EU', 'NA', 'KR'], api_version: Literal['1','2']) -> None:
    #     #  /valorant/:version/by-puuid/mmr/:region/:puuid
    #     ...

    # async def mmr_history(self, name: str, tag:str, region: Literal['AP', 'EU', 'NA', 'KR']) -> None:
    #     #  /valorant/:version/by-puuid/mmr/:region/:puuid
    #     ...

    # async def mmr_history_puuid(self, puuid: str, region: Literal['AP', 'EU', 'NA', 'KR']) -> None:
    #     #  /valorant/v1/by-puuid/mmr-history/:region/:puuid
    #     ...

    # async def match_history(self, name: str, tag:str, region: Literal['AP', 'EU', 'NA', 'KR']) -> None:
    #     #  /valorant/v3/matches/:region/:name/:tag
    #     ...
    
    # async def match_history_puuid(self, puuid: str, region: Literal['AP', 'EU', 'NA', 'KR']) -> None:
    #     #  /valorant/v3/by-puuid/matches/:region/:puuid
    
    #     ...
    # async def match_data(self, match_id: str) -> None:
    #     #  /valorant/v2/match/:matchid
    #     ...

    # async def website_articles(region):
    #     # en-us, en-gb, de-de, es-es fr-fr it-it ru-ru tr-tr es-MX ja-jp ko-kr pt-br
    #     # /valorant/v1/website/:country-code
    #     ...

    # async def server_status(region: Literal['AP', 'EU', 'NA', 'KR']) -> None:
    #     # /valorant/v1/status/:region
    #     ...
    
    # async def content():
    #     ...             
    #     https://api.henrikdev.xyz/valorant/v1/website
    #     # /valorant/v1/content

async def setup(bot) -> None:
    await bot.add_cog(ValorantCommands(bot))
    await bot.add_cog(Notifys(bot))