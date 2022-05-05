import discord
import contextlib
from datetime import datetime, timedelta
from .resources import points, tiers
from utils.formats import format_dt, format_relative
from typing import Union, Dict, List, Any, Optional

# if TYPE_CHECKING:
from .useful import calculate_level_xp, iso_to_time, GetFormat, JSON
from .resources import get_emoji_tier

class Embed(discord.Embed): # Custom Embed
    def __init__(self, description:str = None, color: Union[discord.Color, int] = 0xfd4554, **kwargs: Any) -> discord.Embed:
        super().__init__(description=description, color=color, **kwargs)

class Generate_Embed:

    def __giorgio_embed(skin: Dict) -> discord.Embed:
        uuid, name, price, icon = skin['uuid'], skin['name'], skin['price'], skin['icon']

        embed = Embed(f"{get_emoji_tier(uuid)} **{name}**\n{points['vp']} {price}", color=0x0F1923)
        embed.set_thumbnail(url=icon)
        return embed

    @classmethod
    def store(cls, player: str, offer: Dict, language: str, response: Dict) -> List[discord.Embed]:
        
        data = GetFormat.offer_format(offer, language)

        # from .pillow import generate_image

        # file = generate_image(data)

        store_esponse = response.get('RESPONSE')

        duration = data['duration']
        description = store_esponse.format(username=player, duration=format_relative(datetime.utcnow() + timedelta(seconds=duration)))
        
        embed = Embed(description)
        embeds = [embed]
        [embeds.append(cls.__giorgio_embed(data[skin])) for skin in data if not skin == 'duration']
        
        return embeds

    def mission(player:str, mission: Dict, language:str, response: Dict) -> discord.Embed:
    
        # language
        title_mission = response.get('TITLE')
        title_daily = response.get('DAILY')
        title_weekly = response.get('WEEKLY')
        title_newplayer = response.get('NEWPLAYER')
        clear_all_mission = response.get('NO_MISSION')
        title_Refills = response.get('REFILLS')
        title_daily_reset = response.get('DAILY_RESET')

        data = GetFormat.mission_format(mission, language)

        daily_format = data['daily']
        daily_end = data['daily_end']
        weekly_format = data['weekly']
        weekly_end = data['weekly_end']
        newplayer_format = data['newplayer']
        
        daily = ''.join(daily_format)
        weekly = ''.join(weekly_format)
        newplayer = ''.join(newplayer_format)

        weekly_end_time = ''
        with contextlib.suppress(Exception):
            weekly_end_time = f"{title_Refills.format(duration=format_relative(iso_to_time(weekly_end)))}"
        
        embed = Embed(title=f"**{title_mission}**")
        embed.set_footer(text=player)
        
        if len(daily) != 0:
            embed.add_field(
                name=f"**{title_daily}**",
                value=f"{daily}\n\n{title_daily_reset.format(duration=format_relative(iso_to_time(daily_end)))}",
                inline=False
        )
        if len(weekly) != 0:
            embed.add_field(
                name=f"**{title_weekly}**",
                value=f"{weekly}\n\n{weekly_end_time}",
                inline=False
            )
        if len(newplayer) != 0:
            embed.add_field(
                name=f"**{title_newplayer}**",
                value=f"{newplayer}",
                inline=False
            )
        if len(embed.fields) == 0:
            embed.color = 0x77dd77
            embed.description = clear_all_mission

        return embed

    @classmethod
    def notify_all(cls, name, skin_list) -> discord.Embed:

        embed = Embed(f"Daily store for **{name}** | Remaining {format_dt((datetime.utcnow() + timedelta(seconds=skin_list['duration'])), 'R')}")
        embeds = [embed]

        embeds.append(cls.__giorgio_embed(skin_list['skin1']))
        embeds.append(cls.__giorgio_embed(skin_list['skin2']))
        embeds.append(cls.__giorgio_embed(skin_list['skin3']))
        embeds.append(cls.__giorgio_embed(skin_list['skin4']))

        return embeds

    def __notify_embed(uuid, name, duration, icon) -> discord.Embed:
        embed = discord.Embed(color=0xfd4554)
        embed.description = f"{get_emoji_tier(uuid)} **{name}** is in your daily store!\nRemaining {format_relative(datetime.utcnow() + timedelta(seconds=duration))}"
        embed.set_thumbnail(url=icon)
        embed.timestamp = discord.utils.utcnow()
        return embed

    @classmethod
    async def notify_specified(cls, notify_user: Any, offer: Dict, author: discord.Member, db: Any) -> discord.Embed:
        from .view import Notify

        user_id = author.id

        duration = offer['duration']

        for noti in notify_user:
            if noti['uuid'] == offer['skin1']['uuid']:
                name = offer['skin1']['name']
                uuid = noti['uuid']
                icon = offer['skin1']['icon']
                view = Notify(user_id, uuid, name, db)
                embed = cls.__notify_embed(uuid, name, duration, icon)
                view.message = await author.send(embed=embed, view=view)

            if noti['uuid'] == offer['skin2']['uuid']:
                name = offer['skin2']['name']
                uuid = noti['uuid']
                view = Notify(user_id, uuid, name, db)
                icon = offer['skin2']['icon']
                embed = cls.__notify_embed(uuid, name, duration, icon)
                view.message = await author.send(embed=embed, view=view)

            if noti['uuid'] == offer['skin3']['uuid']:
                name = offer['skin3']['name']
                uuid = noti['uuid']
                icon = offer['skin3']['icon']
                view = Notify(user_id, uuid, name, db)
                embed = cls.__notify_embed(uuid, name, duration, icon)
                view.message = await author.send(embed=embed, view=view)

            if noti['uuid'] == offer['skin4']['uuid']:
                name = offer['skin4']['name']
                uuid = noti['uuid']
                icon = offer['skin4']['icon']
                view = Notify(user_id, uuid, name, db)
                embed = cls.__notify_embed(uuid, name, duration, icon)
                view.message = await author.send(embed=embed, view=view) 

    def battlepass(player:str, data: Dict, season: Dict, language: str, response: Dict) -> discord.Embed:
        from .useful import GetFormat

        # language
        MSG_RESPONSE = response.get('RESPONSE')
        MSG_TIER = response.get('TIER')

        BTP = GetFormat.battlepass_format(data, season, language)

        item = BTP['data']
        reward = item['reward']
        xp = item['xp']
        act = item['act']
        tier = item['tier']
        icon = item['icon']
        season_end = item['end']
        item_type = item['type']

        description = MSG_RESPONSE.format(next=f'`{reward}`', type=f'`{item_type}`', xp=f'`{xp:,}/{calculate_level_xp(tier + 1):,}`', end=format_relative(season_end))

        embed =  Embed(description, title=f"BATTLEPASS")
        
        if icon:
            if item_type in ['PlayerCard', 'Skin']:
                embed.set_image(url=icon)
            else:
                embed.set_thumbnail(url=icon)
        
        if tier >= 50:
            embed.color = 0xf1b82d

        if tier == 55:
            embed.description = f'{reward}'

        embed.set_footer(text=f"{MSG_TIER} {tier} | {act}\n{player}")

        return embed

    def __nightmarket_embed(skins) -> discord.Embed:
        
        uuid, name, icon, price, dpice = skins['uuid'], skins['name'], skins['icon'], skins['price'], skins['disprice']

        embed = Embed(f"{get_emoji_tier(uuid)} **{name}**\n{points['vp']} {dpice} ~~{price}~~", color=0x0F1923)
        embed.set_thumbnail(url=icon)
        return embed

    @classmethod
    def nightmarket(cls, player:str, offer: Dict, language: str, response: Dict) -> discord.Embed:
        
        message_response = response.get('RESPONSE')

        night_mk = GetFormat.nightmarket_format(offer, language, response)
        
        skins = night_mk['nightmarket']
        duration = night_mk['duration']

        description = message_response.format(username=player, duration=format_relative(datetime.utcnow() + timedelta(seconds=duration)))
        embed = Embed(description)

        embeds = [embed]
        [embeds.append(cls.__nightmarket_embed(skins[skin])) for skin in skins]

        return embeds

    # ---------- POINT ---------- #

    def point(player:str, wallet: Dict, language:str, response: Dict) -> discord.Embed:

        # language
        title_point = response.get('POINT')

        # cache = JSON.read('cache')
        # point = cache['currencies']

        vp_uuid = '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'
        rad_uuid = 'e59aa87c-4cbf-517a-5983-6e81511be9b7'

        valorant_point = wallet['Balances'][vp_uuid]
        radiant_point = wallet['Balances'][rad_uuid]
        
        # rad = point[rad_uuid]['names'][language]
        # vp = point[vp_uuid]['names'][language]
        # if vp == 'VP': vp = 'Valorant Points'

        rad = 'Radianite Points'
        vp = 'Valorant Points'

        embed = Embed(title=f"{title_point}:")
        embed.add_field(name=vp, value=f"{points['vp']} {valorant_point}")
        embed.add_field(name=rad, value=f"{points['rad']} {radiant_point}")
        embed.set_footer(text=player)

        return embed