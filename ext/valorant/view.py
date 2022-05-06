from __future__ import annotations

# Standard
import discord
import asyncpg
import contextlib
from discord import Interaction, TextStyle, ButtonStyle
from discord import ui
from discord.ext import menus, commands
from utils.menus import LattePage
from utils.modal import BaseModal

from typing import Optional, List, Union, Dict, Awaitable, Any

# Local
from .useful import GetItem
from .embed import get_emoji_tier
from .resources import points as points_emoji
from .auth import Auth
from .locale import LocaleResponse, LocaleErrorResponse, InteractionLanguage
from .useful import JSON

class share_button(ui.View):
    def __init__(self, interaction: Interaction, embeds: List[discord.Embed]):
        self.interaction = interaction
        self.embeds = embeds
        super().__init__(timeout=300)

    async def on_timeout(self) -> None:
        await self.interaction.edit_original_message(view=None)

    @ui.button(label='Share to friends', style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: Interaction, button: ui.Button):
        await interaction.channel.send(embeds=self.embeds)
        await self.interaction.edit_original_message(content='\u200b', embed=None, view=None)

class Notify(ui.View):
    def __init__(self, user_id: int, uuid: str, name: str, db: asyncpg.Pool) -> None:
        self.user_id = user_id
        self.uuid = uuid
        self.name = name
        self.db = db
        super().__init__(timeout=600)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == int(self.user_id):
            return True
        return False

    async def on_timeout(self) -> None:
        with contextlib.suppress(Exception):
            self.remove_notify.disabled = True
            await self.message.edit_original_message(view=self)

    @ui.button(label='Remove Notify', emoji='✖️', style=discord.ButtonStyle.red)
    async def remove_notify(self, interaction: discord.Interaction, button: ui.Button):

        query = 'DELETE FROM valorant.notifys WHERE user_id = $1 AND uuid = $2;'
        db: asyncpg.Pool = self.db
        await db.execute(query, self.user_id, self.uuid)

        self.remove_notify.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f'**{self.name}** has been removed from notify', ephemeral=True)

class NumberButton(ui.Button):
    def __init__(self, label: str, custom_id: Union[str, int]) -> None:
        super().__init__(
            label=label,
            style=discord.enums.ButtonStyle.red,
            custom_id=str(custom_id)
        )

    async def callback(self, interaction: discord.Interaction) -> None: 

        await interaction.response.defer()
        
        # remove from db
        user_id = self.view.user_id
        query = 'DELETE FROM valorant.notifys WHERE user_id = $1 AND uuid = $2;'
        db: asyncpg.Pool = self.view.db
        await db.execute(query, user_id, self.custom_id)
        
        # remove from view
        del self.view.skin_source[self.custom_id]
        
        # update view
        self.view.update_button()
        embed = self.view.main_embed()
        await self.view.interaction.edit_original_message(embed=embed, view=self.view)

class Notify_list(ui.View):
    def __init__(self, interaction: discord.Interaction, db: asyncpg.Pool, language = 'en-US') -> None:
        self.interaction = interaction
        self.db = db
        self.language = language
        self.user_id = interaction.user.id
        super().__init__(timeout=600)
    
    async def on_timeout(self) -> None:
        embed = discord.Embed(color=0x2F3136, description='🕙 Timeout')
        await self.interaction.edit_original_message(embed=embed, view=None) 
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:        
        if interaction.user == self.interaction.user:
            return True
        await interaction.response.send_message('This pagination menu cannot be controlled by you, sorry!', ephemeral=True)
        return False

    def update_button(self) -> None:
        self.clear_items()
        self.create_button()

    def create_button(self) -> None:
        data = self.skin_source
        for index, skin in enumerate(data, start=1):
            self.add_item(NumberButton(label=index, custom_id=skin))
    
    async def get_row(self) -> Dict:
        user_id =  self.interaction.user.id
        query = 'SELECT uuid FROM valorant.notifys WHERE user_id = $1;'
        row = await self.db.fetch(query, user_id)
        return row

    def get_data(self, row: Dict) -> None:

        notify_skin = row
        
        skin_source:dict = {}

        for skin in notify_skin:
            uuid = skin['uuid']
            get_skin = GetItem.get_skin(uuid)
            name = get_skin['names'][self.language]
            icon = get_skin['icon']
            price = GetItem.get_skin_price(uuid)
            skin_source[uuid] = {
                'name': name,
                'icon':  icon,
                'price': price,
                'emoji': get_emoji_tier(uuid)
            }

        self.skin_source = skin_source

    def main_embed(self) -> discord.Embed:        
        skin_list: dict = self.skin_source
        VP = points_emoji['vp']

        embed = discord.Embed(description='\u200b', title='Your Notify:', color=0xfd4554)
    
        if len(skin_list) == 0:
            embed.description = f"You don't have skin notify"
        else:
            embed.set_footer(text='Click button for remove')
            count = 0
            text_format = []
            for skin in skin_list:
                name = skin_list[skin]['name']
                icon = skin_list[skin]['icon']
                price = skin_list[skin]['price']
                emoji = skin_list[skin]['emoji']
                count += 1
                text_format.append(f"**{count}.** {emoji} **{name}**\n{VP} {price}")
            else:
                embed.description = '\n'.join(text_format)
                if len(skin_list) == 1:
                    embed.set_thumbnail(url=icon)
        
        return embed
    
    async def start(self) -> None:
        row = await self.get_row()
        self.get_data(row)
        self.create_button()
        embed = self.main_embed()

        await self.interaction.response.send_message(embed=embed, view=self)

class TwoFA_UI(ui.Modal, title='Two-factor authentication'):
    '''Modal for riot login with 2 factor authentication'''
    
    def __init__(self, interaction: Interaction, db: asyncpg.Pool, auth: Dict, update:bool, response: Dict) -> None:
        super().__init__(timeout=60)
        self.interaction = interaction
        self.db = db
        self.cookie = auth['cookie']
        self.update: bool = update
        self.response = response
        self.two2fa.placeholder = auth['message']
        self.two2fa.label = auth['label']
    
    two2fa = ui.TextInput(
        label='Input 2FA Code',
        # min_length=6,
        max_length=6,
        style=TextStyle.short
    )

    async def on_submit(self, interaction: Interaction) -> None:

        code = self.two2fa.value
        if code:
            cookie = self.cookie
            user_id = self.interaction.user.id
            auth = Auth()
            auth.locale_code = self.interaction.locale

            async def send_embed(content: str) -> Awaitable[None]:
                embed = discord.Embed(description = content, color=0xfd4554)
                if interaction.response.is_done():
                    return await interaction.followup.send(embed=embed, ephemeral=True)
                await interaction.response.send_message(embed=embed, ephemeral=True)

            if not code.isdigit():
                return await send_embed(f"`{code}` is not a number")
            
            auth = auth.give2facode(code, cookie)

            if auth['auth'] == 'response':
                

                login = await self.db.login(user_id, auth, interaction.guild_id, interaction.locale, self.update)
                if login['auth']:
                    return await send_embed(f"{self.response.get('SUCCESS')} **{login['player']}!**")
                
                return await send_embed(login['error'])
                
            elif auth['auth'] == 'failed':
                return await send_embed(auth['error'])
    
    async def on_error(self, error: Exception, interaction: Interaction) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True) 

class TwoFA_UI_Temp(ui.Modal, title='Two-factor authentication'):
    '''Modal for riot login with 2 factor authentication'''
    
    def __init__(self, interaction: Interaction, db:asyncpg.Pool, auth: Dict, update:bool, response: Dict) -> None:
        super().__init__(timeout=60)
        self.interaction = interaction
        self.db = db
        self.cookie = auth['cookie']
        self.update: bool = update
        self.response = response
        self.two2fa.placeholder = auth['message']
    
    two2fa = ui.TextInput(
        label='Input 2FA Code',
        max_length=6,
        style=TextStyle.short
    )

    async def on_submit(self, interaction: Interaction) -> None:

        code = self.two2fa.value
        if code:
            cookie = self.cookie
            user_id = self.interaction.user.id
            auth = Auth()

            async def send_embed(content: str) -> Awaitable[None]:
                embed = discord.Embed(description = content, color=0xfd4554)
                if interaction.response.is_done():
                    return await interaction.followup.send(embed=embed, ephemeral=True)
                await interaction.response.send_message(embed=embed, ephemeral=True)

            if not code.isdigit():
                return await send_embed(f"`{code}` is not a number")
            
            auth = auth.give2facode(code, cookie)

            if auth['auth'] == 'response':
                ...
                # login = await self.db.login(user_id, auth, interaction.guild_id, self.update)
                # if login['auth']:
                #     return await send_embed(f"{self.response.get('SUCCESS')} **{login['player']}!**")
                
                # return await send_embed(login['error'])
                
            elif auth['auth'] == 'failed':
                ...
                # return await send_embed(auth['error'])
    
    async def on_error(self, error: Exception, interaction: Interaction) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True) 

class SearchSourcePage(menus.ListPageSource):
    async def format_page(self, menu, entries) -> None:
        pages = []
        for index, entry in enumerate(entries, start=menu.current_page * self.per_page):
            pages.append(entry)

        maximum = self.get_max_pages()
        if maximum > 1:
            footer = f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} players)'
            menu.embed.set_footer(text=footer)

        menu.embed.description = '\n'.join(pages)
        return menu.embed

class SearchPages(LattePage):
    def __init__(self, entries, *, interaction: discord.Interaction, per_page: int = 12, ephemeral: bool = False):
        super().__init__(SearchSourcePage(entries, per_page=per_page), interaction=interaction, ephemeral=ephemeral, compact=True)
        self.embed = discord.Embed(color=0xfd4554)

class LeaderboardView(LattePage):

    search_prompter: Optional[LeaderboardView.SearchPrompt] = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(self.search)
        self.remove_item(self.stop_pages)
    
    class SearchPrompt(BaseModal):
        search_player = ui.TextInput(label="Search Player", placeholder='player...', min_length=1, max_length=21, required=True)

        def __init__(self, view: LattePage) -> None:
            super().__init__(title=f"Player name to search...")
            self.view = view
            self.valid = False
            self.interaction = view.interaction
            self.source = view.source

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            # extra measures, there isn't a way for this to trigger.
            if interaction.user == self.interaction.user:
                return True
            await interaction.response.send_message("You can't fill up this modal.", ephemeral=True)
        
        async def on_submit(self, interaction: discord.Interaction) -> None:
            value = self.search_player.value.strip()

            player_list = []
            
            for page in range(self.source.get_max_pages()):
                current: List = await self.source.get_page(page)
                get_player = self.view.get_player_from_entry(value, current)
                if get_player:
                    player_format = get_player[0]
                    player_list.append(player_format)

            if value.lower() == "cancel":
                return
            
            if player_list:
                p = SearchPages(player_list, interaction=interaction, ephemeral=True)
                p.remove_item(p.stop_pages)
                return await p.start() 
            
    def get_player_from_entry(self, keyword: str, entry: str) -> Optional[List[str]]:
        '''Seach player from leaderboard'''

        player_find = []

        for find in entry:
            player = find.split('> ')[1].split(' - ')
            # if not player[0] == 'Secret Agent':
            player_split_tag = player[0].split('#')
            for name in player_split_tag:
                if keyword.lower() in name.lower(): #get_close_matches(keyword, player_split_tag) 
                    player_find.append(find)
        
        return player_find

    @ui.button(label='\N{RIGHTWARDS ARROW WITH HOOK} \u200b Search...', style=ButtonStyle.primary)
    async def search(self, interaction:Interaction, button:ui.Button) -> None:

        if self.search_prompter is None:
            self.search_prompter = self.SearchPrompt(self)

        return await interaction.response.send_modal(self.search_prompter)

class LeaderboardPageSource(menus.ListPageSource):
    
    async def format_page(self, menu, entries):
        pages = []
        
        radiant_color = 0xffffaa
        immortal_color = 0xfd4554
        radiant_count = 0
        for entry in entries:
            if 'radiant' in entry: radiant_count += 1
            pages.append(entry)

        menu.embed.color = radiant_color if radiant_count >= 6 else immortal_color
        maximum = self.get_max_pages()
        if maximum > 1:
            footer = f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} players)'
            menu.embed.set_footer(text=footer)

        menu.embed.description = '\n'.join(pages)
        return menu.embed

class LeaderboardPages(LeaderboardView):
    def __init__(self, entries, *, interaction: discord.Interaction, per_page: int = 12):
        super().__init__(LeaderboardPageSource(entries, per_page=per_page), interaction=interaction)
        self.embed = discord.Embed()

# inspired by https://github.com/giorgi-o
class BaseBundle(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, entries: Dict, response: Dict, language: str) -> None:
        self.interaction = interaction
        self.entries = entries
        self.response = response
        self.language = language
        self.bot: commands.Bot = getattr(interaction, "client", interaction._state._get_client())
        self.current_page: int = 0
        self.embeds: List[List[discord.Embed]] = []
        self.page_format = {}
        super().__init__()
        self.clear_items()
        
    def fill_items(self, force=False) -> None:
        self.clear_items()
        if len(self.embeds) > 1 or force:
            self.add_item(self.back_button)
            self.add_item(self.next_button)

    def base_embed(self, title:str, description:str, icon:str, color: int=0x0F1923) -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_thumbnail(url=icon)
        return embed

    def build_embeds(self) -> None:

        vp_emoji = points_emoji.get('vp')
    
        embeds_list = []
        embeds = []

        collection_title = self.response.get('TITLE')
        
        bundle = self.entries

        try:
            bundle_item = sorted(bundle['items'], key=lambda x: x['price'], reverse=True)
        except Exception:
            bundle_item = bundle['items']
        
        embeds.append(discord.Embed(title=bundle['names'][self.language] + f" {collection_title}", description=f"{vp_emoji} {bundle['price'] or '-'}",color=0xfd4554).set_image(url=bundle['icon']))
        
        if bundle_item:
        # for items in sorted(bundle['items'], key=lambda x: x['price'], reverse=True):
            for items in bundle_item:
                item = GetItem.Get_by_type(items['type'], items['uuid'])
                item_type = GetItem.get_type_name(items['type'])

                emoji = get_emoji_tier(items['uuid']) if item_type == 'Skins' else ''
                icon = item['icon'] if item_type != 'Player Cards' else item['icon']['large']
                color = 0xfd4554 if item_type == 'Skins' else 0x0F1923
            
                embed = self.base_embed(f"{emoji} {item['names'][self.language]}", f"{vp_emoji} {items['price'] or '-'}", icon, color)
                embeds.append(embed)

                if len(embeds) == 10:
                    embeds_list.append(embeds)
                    embeds = []

        if len(embeds) != 0:
            embeds_list.append(embeds)

        self.embeds = embeds_list

    def build_Featured_Bundle(self, bundle: List[Dict]) -> List[discord.Embed]:
        vp_emoji = points_emoji.get('vp')

        name = bundle['names'][self.language]

        featured_bundle_title = self.response.get('TITLE')
        embed = discord.Embed(title=featured_bundle_title.format(bundle=name), description=f"{vp_emoji} **{bundle['price']}** ~~{bundle['base_price']}~~",color=0xfd4554).set_image(url=bundle['icon'])

        embed_list = []

        embeds = [embed]

        for items in sorted(bundle['items'], reverse=True, key=lambda c: c['base_price']):
            item = GetItem.Get_by_type(items['type'], items['uuid'])
            item_type = GetItem.get_type_name(items['type'])
            emoji = get_emoji_tier(items['uuid']) if item_type == 'Skins' else ''
            icon = item['icon'] if item_type != 'Player Cards' else item['icon']['large']
            color = 0xfd4554 if item_type == 'Skins' else 0x0F1923
            embed = self.base_embed(f"{emoji} {item['names'][self.language]}", f"**{vp_emoji} {items['price']}** ~~{items['base_price']}~~", icon, color)
            embeds.append(embed)

            if len(embeds) == 10:
                embed_list.append(embeds)
                embeds = []
        
        if len(embeds) != 0:
            embed_list.append(embeds)

        return embed_list

    @ui.button(label='Back')
    async def back_button(self, interaction: Interaction, button: ui.Button):
        self.current_page = 0
        embeds = self.embeds[self.current_page]
        self.update_button()
        await interaction.response.edit_message(embeds=embeds, view=self)
        
    @ui.button(label='Next')
    async def next_button(self, interaction: Interaction, button: ui.Button):
        self.current_page = 1
        embeds = self.embeds[self.current_page]
        self.update_button()
        await interaction.response.edit_message(embeds=embeds, view=self)

    def update_button(self):
        self.next_button.disabled = self.current_page == len(self.embeds) - 1
        self.back_button.disabled = self.current_page == 0

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        await interaction.response.send_message('This menus cannot be controlled by you, sorry!', ephemeral=True)
        return False
        
    async def start(self) -> None:
        self.build_embeds()
        self.fill_items()
        self.update_button()
        embeds = self.embeds[0]
        return await self.interaction.followup.send(embeds=embeds, view=self)
    
    async def start_furture(self) -> None:
        FBundle = self.entries['FeaturedBundle']['Bundle']

        get_bundle = GetItem.get_bundle(FBundle["DataAssetID"])

        bundle_payload = {
            "uuid": FBundle["DataAssetID"],
            "icon": get_bundle['icon'],
            "names": get_bundle['names'],
            "duration": FBundle["DurationRemainingInSeconds"],
            "items": []
        }

        price = 0
        baseprice = 0

        for items in FBundle['Items']:
            item_payload = {
                "uuid": items["Item"]["ItemID"],
                "type": items["Item"]["ItemTypeID"],
                "item" : GetItem.Get_by_type(items["Item"]["ItemTypeID"], items["Item"]["ItemID"]),
                "amount": items["Item"]["Amount"],
                "price": items["DiscountedPrice"],
                "base_price": items["BasePrice"],
                "discount": items["DiscountPercent"]
            }
            price += int(items["DiscountedPrice"])
            baseprice += int(items["BasePrice"])
            bundle_payload['items'].append(item_payload)

        bundle_payload['price'] = price
        bundle_payload['base_price'] = baseprice

        self.embeds = self.build_Featured_Bundle(bundle_payload)
        self.fill_items()
        self.update_button()
        await self.interaction.followup.send(embeds=self.embeds[0], view=self)


class AgentInfoView(ui.View):

    def __init__(self, interaction: Interaction):
        self.interaction = interaction
        super().__init__()

    async def start(self, agent_uuid: str = None) -> None:
        
        if agent_uuid is None:
            data = JSON.read('agents')
            agent = data[agent_uuid]
            language = InteractionLanguage(self.interaction.locale)

            name = agent['names'][language]
            descriptions = agent['descriptions'][language]
            icon = agent['icon']['icon']
            portraitv2 = agent['icon']['portraitv2']
            color = agent['icon']['color']

            embed = discord.Embed(title=name, description=descriptions, color=0x0F1923)
            embed.set_thumbnail(url=icon)

            await self.interaction.response.send_message(embed=embed, view=self)

class Confirm(discord.ui.View):
    def __init__(self, interaction: Interaction):
        super().__init__(timeout=60)
        self.value = None
        self.interaction = interaction
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        await interaction.response.send_message('This menus cannot be controlled by you, sorry!', ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(content='Timed out!', view=None)

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()

class WeasponView(ui.View):
    def __init__(self, interaction: Interaction, source: List[List[discord.Embed]], other_view: ui.View) -> None:
        self.interaction = interaction
        self.source = source
        self.other_view = other_view
        self.current_page = 0
        self.max_page = len(source)
        super().__init__(timeout=600)
        self._update_buttons()

    def _update_buttons(self) -> None:
        page = self.current_page
        total = self.max_page - 1
        self.next_page.disabled = page == total
        self.back_page.disabled = page == 0
        self.first_page.disabled = page == 0
        self.last_page.disabled = page == total

    async def show_page(self, interaction: Interaction, page_number: int) -> None:
        try:
            if page_number <= 1 and page_number != 0:
                page_number = self.current_page + page_number
            self.current_page = page_number
            self._update_buttons()
            embeds = [embed for embed in self.source[self.current_page]]
            await interaction.response.edit_message(embeds=embeds, view=self)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass
        
    @ui.button(label='≪', style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_page(interaction, 0)

    @ui.button(label='Back', style=discord.ButtonStyle.blurple)
    async def back_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_page(interaction, - 1)
    
    @ui.button(label='Next', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_page(interaction, +1)

    @ui.button(label='≫', style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_page(interaction, self.max_page - 1)
    
    # @ui.select(placeholder='CHANGE SKIN')
    # async def select_change_skin(self, interaction: discord.Interaction, option: discord.SelectOption):
    #     await self.interaction.response.edit_message(embeds=[option.description], view=self)

    # def build_select(self):
    #     self.select_change_skin.options = []
    #     loadout = self.other_view.loadout
    #     for weapon in loadout['weapons']:
    #         self.select_change_skin.add_option(label=weapon['weapon'], description=weapon['name'])

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        return False
    
    async def on_timeout(self) -> None:
        await self.interaction.delete_original_message()

    async def start(self):
        # self.build_select()
        embeds = [embed for embed in self.source[0]]
        await self.interaction.response.send_message(embeds=embeds, view=self, ephemeral=True)

class InventoryView(ui.View):
    def __init__(self, interaction: Interaction, player_loadout: dict, endpoint: Any, raw_loadout: dict, language: str) -> None:
        self.interaction = interaction
        self.loadout = player_loadout
        self.endpoint = endpoint
        self.raw_loadout = raw_loadout
        self.language = language
        self.sprays_page = []
        self.skin_page = []
        from itertools import cycle
        card_type = ['wide','large', 'small']
        self.card_type_cycle = cycle(card_type)
        super().__init__()

    # @ui.button(label='Player Card')
    # async def card_button(self, interaction:Interaction, button: ui.Button):
    #     ...

    # @ui.button(label='testing')
    # async def testing_button(self, interaction:Interaction, button: ui.Button):
    #     endpoint = self.endpoint
    #     # {'Subject': '47bbe7de-0d6c-5c3d-978f-1c2bb529ed7d', 'Version': 1143, 'Guns': [{'ID': '63e6c2b6-4a8e-869c-3d4c-e38355226584', 'SkinID': '57523cf0-4574-968b-9f17-168e3bdb6d0d', 'SkinLevelID': '162beb92-4ab7-4383-da51-4b94ba90bd5d', 'ChromaID': '156158a5-4eb2-79ef-49e9-16a680fe93a9', 'Attachments': []}, {'ID': '55d8a0f4-4274-ca67-fe2c-06ab45efdf58', 'SkinID': '5305d9c4-4f46-fbf4-9e9a-dea772c263b5', 'SkinLevelID': '0f5f60f4-4c94-e4b2-ceab-e2b4e8b41784', 'ChromaID': 'b33de820-4061-8b85-31ce-808f1a2c58f5', 'Attachments': []}, {'ID': '9c82e19d-4575-0200-1a81-3eacf00cf872', 'SkinID': '437307c6-424c-6a48-9738-949b91166353', 'SkinLevelID': '9ed2bd1c-46b9-fdf5-b445-5f91d82fc441', 'ChromaID': '5d94fbe1-434e-990d-1d51-2ca483c3abe4', 'CharmInstanceID': '159bb322-dd4a-4899-9a17-ef9fd6421432', 'CharmID': '0911b78d-48a7-fb01-3ccd-0ca9a3996f75', 'CharmLevelID': 'a4e3fe97-4de9-c133-7dd0-f2b294a2ead2', 'Attachments': []}, {'ID': 'ae3de142-4d85-2547-dd26-4e90bed35cf7', 'SkinID': '4e6341f9-4851-603d-daff-9185f007d3dc', 'SkinLevelID': '6f86d77a-43c6-17b5-312f-87bf159076d9', 'ChromaID': 'e455f87b-4afc-f2ea-22de-5ab5fe7ef7f5', 'Attachments': []}, {'ID': 'ee8e8d15-496b-07ac-e5f6-8fae5d4c7b1a', 'SkinID': '44b7b110-46bf-ccbb-2613-29a5df296461', 'SkinLevelID': 'ed4773ba-465d-6501-701a-e39d1ba0b97a', 'ChromaID': 'c805c92a-4424-69f2-a0f2-8c8c9bb33a4a', 'CharmInstanceID': 'c94cb3ad-bc08-4869-b10f-f35c85cc6262', 'CharmID': 'd400dd1a-4a81-1b26-b8f1-a994e13739b2', 'CharmLevelID': '58584a97-4839-3cb0-6f21-02809648df92', 'Attachments': []}, {'ID': 'ec845bf4-4f79-ddda-a3da-0db3774b2794', 'SkinID': '3d8f9c7d-4259-4710-1f94-0fbc4f25035c', 'SkinLevelID': '2a25f841-4769-6536-ded3-8890ee26c430', 'ChromaID': '0256ac78-466b-ea4a-4bdf-c3908c0e7e83', 'Attachments': []}, {'ID': '910be174-449b-c412-ab22-d0873436b21b', 'SkinID': '26582dc8-43dd-15b6-a31c-739b90302bea', 'SkinLevelID': '23885a08-4a77-82a7-5dbc-ec812f252ca0', 'ChromaID': '57e0882d-44c2-c87a-f9ee-10a6fd156da8', 'CharmInstanceID': '5172b74a-6267-42f0-9bc7-669cc9ab110f', 'CharmID': '1e909ee9-4af5-5d50-aa27-2bb596187986', 'CharmLevelID': '5b863cb9-4e41-ec89-69ee-49a223d05ff1', 'Attachments': []}, {'ID': '44d4e95c-4157-0037-81b2-17841bf2e8e3', 'SkinID': 'f67d4d78-4567-f8ca-010b-18919c49aa05', 'SkinLevelID': 'fe7ac291-4516-02d4-9101-0a990615a585', 'ChromaID': 'c4db17ef-4610-90e6-1e8c-688b3a5aac71', 'CharmInstanceID': 'fbefb1cd-d7e6-4485-904b-bf8b237fc823', 'CharmID': '58de9852-48ef-57f8-d6f0-8a885b4c27b0', 'CharmLevelID': 'a0a1a09a-45df-0373-96a5-d08c6852f47f', 'Attachments': []}, {'ID': '29a0cfab-485b-f5d5-779a-b59f85e204a8', 'SkinID': '47d5e54a-48e5-b62a-5cf5-3cb7efc12e90', 'SkinLevelID': 'bbbe4b32-457c-e4fb-a674-1d9c3885d331', 'ChromaID': '528232a1-4d11-e724-5c1b-b3bb0c392c84', 'CharmInstanceID': 'fb95344a-40dc-430f-9cfa-023a56872771', 'CharmID': '67310368-40c0-75fc-4853-3192ddf3011a', 'CharmLevelID': '3ddb3c27-4cf6-59ed-8e17-0e9ab970efb4', 'Attachments': []}, {'ID': '1baa85b4-4c70-1284-64bb-6481dfc3bb4e', 'SkinID': '4725c2c4-45b7-d9ab-ff4f-a79c3b2dd9ec', 'SkinLevelID': '55aaa4ee-4d64-51c7-3c09-fd9bcbe1d122', 'ChromaID': 'b6812d54-4e43-5daa-0b19-5884e5a3e9ca', 'CharmInstanceID': '2f747e8b-cc20-4c5e-bbc7-5e2c15faa3ef', 'CharmID': '42cb4b6a-45e3-8a83-2f52-0d90c7ca306d', 'CharmLevelID': 'd88fa813-4ade-1585-0865-90be2c984214', 'Attachments': []}, {'ID': 'e336c6b8-418d-9340-d77f-7a9e4cfe0702', 'SkinID': '84d840c5-4479-4395-d823-e7acbe634c5e', 'SkinLevelID': '114a5ce1-43ac-2cd8-3a9a-adbdfa32220e', 'ChromaID': 'e93656e2-42f9-8eb1-8b74-e5829f3eb08e', 'CharmInstanceID': '2f6a299a-53e2-5fe8-8054-eda465ab86bb', 'CharmID': '237f36ef-40d5-410a-84be-6c896aad6fde', 'CharmLevelID': '9ba23ae7-4e2f-635e-f6c3-159eb91414cc', 'Attachments': []}, {'ID': '42da8ccc-40d5-affc-beec-15aa47b42eda', 'SkinID': '310b80d8-4e1b-b4f0-b713-9dad458ce734', 'SkinLevelID': 'f9688e62-42c5-9f10-f160-49abaee2e02c', 'ChromaID': 'eb54deca-4ae4-07c5-f506-8f9f2ec6331b', 'CharmInstanceID': '9b9065c4-8c18-4004-85e0-2ec675b8abcb', 'CharmID': '67310368-40c0-75fc-4853-3192ddf3011a', 'CharmLevelID': '3ddb3c27-4cf6-59ed-8e17-0e9ab970efb4', 'Attachments': []}, {'ID': 'a03b24d3-4319-996d-0f8c-94bbfba1dfc7', 'SkinID': 'd1f2920f-469a-3431-ad96-96afbd0017f2', 'SkinLevelID': '88cba358-4f4d-4d0e-69fc-b48f4c65cb2d', 'ChromaID': '4914f50d-49f9-6424-ca80-9486c45a138d', 'CharmInstanceID': 'c00335d6-7423-5727-a0f2-7b67110c4635', 'CharmID': 'e2e5ab96-4103-8473-14a7-8d8321a3ae6e', 'CharmLevelID': 'f470ff75-4f99-c13a-5819-0b8cc78ad839', 'Attachments': []}, {'ID': '4ade7faa-4cf1-8376-95ef-39884480959b', 'SkinID': '2d5e6025-4166-730e-1024-abb766d19568', 'SkinLevelID': '6672800e-442c-a0b5-92d3-ed83483f04df', 'ChromaID': '09ad889f-4f6b-038e-9b72-23a8203f393f', 'Attachments': 
    #     # []}, {'ID': 'c4883e50-4494-202c-3ec3-6b8a9284f00b', 'SkinID': '51da27fe-4a3f-016a-d18d-b68a47545f6f', 'SkinLevelID': '3e0a3431-4e78-89d1-ee57-d9837e324ee0', 'ChromaID': '4156c0b0-44b8-7ea9-6707-75aec36ec5fb', 'Attachments': []}, {'ID': '462080d1-4035-2937-7c09-27aa2a5c27a7', 'SkinID': '6196c91c-4f0a-2aa2-342a-6fbac6d4ec3c', 'SkinLevelID': '5172ea04-432f-2bfb-2163-808ccc2442c3', 'ChromaID': 'a018e4a4-4049-731a-ba49-74ac2b7f5626', 'CharmInstanceID': 'bab80dec-1a26-4f23-9f8f-a23544082975', 'CharmID': '90c69d6b-4cd2-9d0c-8c3f-ada26e881ea9', 'CharmLevelID': '2497a841-4545-f706-f6a5-c086d0713a75', 'Attachments': []}, {'ID': 'f7e1b454-4ad4-1063-ec0a-159e56b58941', 'SkinID': '46c8b165-4ba5-d42c-79e9-4fba8951ca48', 'SkinLevelID': '0329743b-4ce8-be9f-b531-f4aadc890287', 'ChromaID': '6d4c4e7b-4936-166b-f4c2-e8b01b5130fc', 'CharmInstanceID': 'bbfeb337-df5b-4e4c-b102-45ac52b47632', 'CharmID': 'b9926112-49d0-b049-b078-798851912eb7', 'CharmLevelID': 'ffa13bca-4bb7-5f3e-48a3-4e96c05a2df9', 'Attachments': []}, {'ID': '2f59173c-4bed-b6c3-2191-dea9b58be9c7', 'SkinID': 'ccde2f25-4525-ef52-e1f0-bd88184bd4a4', 'SkinLevelID': 'c01062ab-48ed-11a2-46bb-dba096daca59', 'ChromaID': 'eee262ad-4f92-7b0d-3b64-d48836a11757', 'Attachments': []}], 'Sprays': [{'EquipSlotID': '5863985e-43ac-b05d-cb2d-139e72970014', 'SprayID': 'a8ea5a21-4dba-be95-6839-89ba93be84b6', 'SprayLevelID': None}, {'EquipSlotID': '0814b2fe-4512-60a4-5288-1fbdcec6ca48', 'SprayID': 'cd3d4242-4282-9210-f34f-9998e8b1f9e0', 'SprayLevelID': 
    #     # None}, {'EquipSlotID': '04af080a-4071-487b-61c0-5b9c0cfaac74', 'SprayID': 'e3b99844-449a-d21b-0612-8c95e74d7d9f', 'SprayLevelID': None}], 'Identity': {'PlayerCardID': '4ca63988-4ca6-2911-a1b5-98a4b765dffd', 'PlayerTitleID': 'fc78400c-4356-c491-ab14-3dbb9e481073', 'AccountLevel': 0, 'PreferredLevelBorderID': 'ebc736cd-4b6a-137b-e2b0-1486e31312c9', 'HideAccountLevel': True}, 'Incognito': True}

    #     # data = {'Subject': f'{endpoint.puuid}', 'Version': 1143, 'Guns': [{
    #     #     "ID"         : "9c82e19d-4575-0200-1a81-3eacf00cf872",
    #     #     "SkinID"     : "b9ee2457-481c-6776-3f5b-0ca8e8f90c89",
    #     #     "SkinLevelID": "fc332008-475f-5555-0155-4cb3bce714ff",
    #     #     "ChromaID"   : "cd3ebdc1-4858-efda-6cee-c683726f8ca9",
    #     #     "Attachments": []
    #     # }], 'Sprays': None, 'Identity': {'PlayerCardID': '00000000-0000-0000-0000-000000000000', 'PlayerTitleID': '00000000-0000-0000-0000-000000000000', 'AccountLevel': 0}, 'Incognito': False}
    #     # raw_version = self.raw_loadout['Version']
    #     # # version = raw_version + 1
    #     # self.raw_loadout['Version'] = version

    #     self.raw_loadout['Guns'] = {
    #         "ID"         : "9c82e19d-4575-0200-1a81-3eacf00cf872",
    #         "SkinID"     : "b9ee2457-481c-6776-3f5b-0ca8e8f90c89",
    #         "SkinLevelID": "fc332008-475f-5555-0155-4cb3bce714ff",
    #         "ChromaID"   : "ad2b0b8b-4da8-9c88-331a-028f2026ab66",
    #         "Attachments": []
    #     }

    #     # print(self.raw_loadout)

    #     # data = {'Subject': f'testing', 'Version': version, 'Guns': {
    #     #     "ID"         : "9c82e19d-4575-0200-1a81-3eacf00cf872",
    #     #     "SkinID"     : "b9ee2457-481c-6776-3f5b-0ca8e8f90c89",
    #     #     "SkinLevelID": "fc332008-475f-5555-0155-4cb3bce714ff",
    #     #     "ChromaID"   : "cd3ebdc1-4858-efda-6cee-c683726f8ca9",
    #     #     "Attachments": []
    #     # }, 'Sprays': None, 'Identity': {'PlayerCardID': '00000000-0000-0000-0000-000000000000', 'PlayerTitleID': '00000000-0000-0000-0000-000000000000', 'AccountLevel': 0}, 'Incognito': True}

    #     # data = json.dumps(data)

    #     await endpoint.put_player_loadout(self.raw_loadout)
    
    # @ui.button(label='Sprays')
    # async def sprays_button(self, interaction:Interaction, button: ui.Button):
    #     ...

    # @ui.button(label='Active', style=ButtonStyle.gray, disabled=True)
    # async def active_button(self, interaction:Interaction, button: ui.Button):
    #     ...

    # spray_inventory = endpoint.store_fetch_entitlements('d5f120f8-ff8c-4aac-92ea-f2b5acbe9475')
    # buddies_inventory = endpoint.store_fetch_entitlements('dd3bf334-87f3-40bd-b043-682a57a8dc3a')
    # card_inventory = endpoint.store_fetch_entitlements('3f296c07-64c3-494c-923b-fe692a4fa1bd')
    # skins_inventory = endpoint.store_fetch_entitlements('e7c63390-eda7-46e0-bb7a-a6abdacd2433')
    # chromas_inventory = endpoint.store_fetch_entitlements('3ad1b2b2-acdb-4524-852f-954a76ddae0a')
    # titles_inventory = endpoint.store_fetch_entitlements('de7caa6b-adf7-4588-bbd1-143831e786c6')
    # agent_inventory = endpoint.store_fetch_entitlements('01bb38e1-da47-4e6a-9b3d-945fe4655707')
    # contract_inventory = endpoint.store_fetch_entitlements('f85cb6f7-33e5-4dc8-b609-ec7212301948')

    # @ui.select(placeholder='select a inventory', row=1, options=[
    #     discord.SelectOption(label='Skins'),
    #     discord.SelectOption(label='Sprays'),
    #     discord.SelectOption(label='Buddies'),
    #     discord.SelectOption(label='Cards'),
    #     # discord.SelectOption(label='chromas'),
    #     discord.SelectOption(label='Titles'),
    # ])
    # async def inventory_select(self, interaction:Interaction, select: ui.Select):
    #     if select.values[0] == 'Skins':
    #         data = self.endpoint.store_fetch_entitlements('e7c63390-eda7-46e0-bb7a-a6abdacd2433')

    #         import json
    #         print(json.dumps(data, indent=4, ensure_ascii=False))
    #         # skins = []
    #         # for skin in data['Entitlements']:
    #         #     item = GetItem.get_skin(skin['ItemID'])
    #         #     skins.append(item)

    #         # print(skins)
    #         # await interaction.response.send_message(skins)

    #     elif select.values[0] == 'Sprays':
    #         data = self.endpoint.store_fetch_entitlements('d5f120f8-ff8c-4aac-92ea-f2b5acbe9475')

    #         for spray in data['Entitlements']:
    #             item = GetItem.get_spray(spray['ItemID'])

    #     elif select.values[0] == 'Buddies':
    #         data = self.endpoint.store_fetch_entitlements('dd3bf334-87f3-40bd-b043-682a57a8dc3a')

    #         for buddy in data['Entitlements']:
    #             item = GetItem.get_buddie(buddy['ItemID'])

    #     elif select.values[0] == 'Cards':
    #         data = self.endpoint.store_fetch_entitlements('3f296c07-64c3-494c-923b-fe692a4fa1bd')

    #         for card in data['Entitlements']:
    #             item = GetItem.get_playercard(card['ItemID'])

    #     elif select.values[0] == 'chromas':
    #         data = self.endpoint.store_fetch_entitlements('3ad1b2b2-acdb-4524-852f-954a76ddae0a')
    #     elif select.values[0] == 'Titles':
    #         data = self.endpoint.store_fetch_entitlements('de7caa6b-adf7-4588-bbd1-143831e786c6')
            
    #         for title in data['Entitlements']:
    #             item = GetItem.get_title(title['ItemID'])

    @ui.button(emoji='🔫', style=ButtonStyle.primary)
    async def weapon_button(self, interaction:Interaction, button: ui.Button):
        self.build_page()
        embeds_list = self.skin_page
        view = WeasponView(interaction, embeds_list, self)
        await view.start()

    @ui.button(emoji='<:spray:971941939190595667>', style=ButtonStyle.primary)
    async def sprays_active(self, interaction:Interaction, button: ui.Button):
        loadout = self.loadout
        embeds = []

        for spray in sorted(loadout['sprays'], key=lambda c: c['slot']):
            embed = discord.Embed(description=f"**{spray['slot']}. {spray['name']}**", color=discord.Color.blurple())
            embed.set_thumbnail(url=spray['icon'])
            embeds.append(embed)
        
        await interaction.response.send_message(embeds=embeds, ephemeral=True)

    @ui.button(label='⟳', style=ButtonStyle.primary)
    async def switch_card(self, interaction:Interaction, button: ui.Button):
        embed = self.main_page()
        await interaction.response.edit_message(embed=embed, view=self)

    # @ui.button(label='Inventory', style=ButtonStyle.gray, disabled=True, row=1)
    # async def inventory_button(self, interaction:Interaction, button: ui.Button):
    #     ...

    # skins_inventory = endpoint.store_fetch_entitlements('e7c63390-eda7-46e0-bb7a-a6abdacd2433')
    # spray_inventory = endpoint.store_fetch_entitlements('3f296c07-64c3-494c-923b-fe692a4fa1bd')
    # buddies_inventory = endpoint.store_fetch_entitlements('dd3bf334-87f3-40bd-b043-682a57a8dc3a')
    # card_inventory = endpoint.store_fetch_entitlements('3f296c07-64c3-494c-923b-fe692a4fa1bd')
    # chromas_inventory = endpoint.store_fetch_entitlements('3ad1b2b2-acdb-4524-852f-954a76ddae0a')
    # titles_inventory = endpoint.store_fetch_entitlements('de7caa6b-adf7-4588-bbd1-143831e786c6')

    # @ui.button(emoji='🔫', style=ButtonStyle.primary, row=1)
    # async def skins_inventory(self, interaction:Interaction, button: ui.Button):
    #     ...
    
    # @ui.button(emoji='<:spray:971941939190595667>', style=ButtonStyle.primary, row=1)
    # async def spray_inventory(self, interaction:Interaction, button: ui.Button):
    #     ...
    
    # @ui.button(emoji='<:buddies:971945838949593108>', style=ButtonStyle.primary, row=1)
    # async def buddies_inventory(self, interaction:Interaction, button: ui.Button):
    #     ...
    
    # @ui.button(emoji='<:card:971944987996590111>', style=ButtonStyle.primary, row=1)
    # async def card_inventory(self, interaction:Interaction, button: ui.Button):
    #     ...
    
    # @ui.button(emoji='<:title:971946769518850108>', style=ButtonStyle.primary, row=1)
    # async def titles_inventory(self, interaction:Interaction, button: ui.Button):
    #     ...

    # @ui.button(label='Chromas Inventory', emoji='🔫', style=ButtonStyle.primary, row=1)
    # async def chromas_inventory(self, interaction:Interaction, button: ui.Button):
    #     ...

    def build_page(self):
        loadout = self.loadout
        skin_list = []
        
        def sort_type(skin):
            if skin['type'] == 'malee':
                return -1
            elif skin['type'] == 'sidearms':
                return 0
            elif skin['type'] == 'smgs':
                return 1
            elif skin['type'] == 'shotgun':
                return 2
            elif skin['type'] == 'rifles':
                return 3
            elif skin['type'] == 'sniper':
                return 4
            return 5

        def populate_weapon(skin):
            if skin['weapon'] == 'Melee':
                return -1
            elif skin['weapon'] == 'Vandal':
                return 0
            elif skin['weapon'] == 'Phantom':
                return 1
            elif skin['weapon'] == 'Operator':
                return 2
            elif skin['weapon'] == 'Sheriff':
                return 3
            elif skin['weapon'] == 'Spectre':
                return 4
            return sort_type(skin) + 5    

        for skin in sorted(loadout['weapons'], key=populate_weapon):

            name = skin['name']
            icon = skin['icon']
            weapon = skin['weapon']
            emoji = skin['emoji']
            color = skin['color']
            weapon_type = skin['type']
    
            embed = discord.Embed(color=color)

            embed.description = f'{emoji} **{name}**'
            embed.set_thumbnail(url=icon)
            embed.set_footer(text=weapon)
            
            skin_list.append(embed)
            if len(skin_list) == 6:
                self.skin_page.append(skin_list)
                skin_list = []
        
        if len(skin_list) > 0:
            self.skin_page.append(skin_list)
        
    def main_page(self):
        from utils.utils import get_dominant_color
        icon = self.loadout['playercard']['icon'][next(self.card_type_cycle)]
        title = self.loadout['playertitle']['names'][self.language]

        embed = discord.Embed(title=title, color=get_dominant_color(icon))
        embed.set_author(name=self.endpoint.player)
        embed.set_image(url=icon)

        return embed

    async def start(self):
        embed = self.main_page()
        await self.interaction.followup.send(embed=embed, view=self)