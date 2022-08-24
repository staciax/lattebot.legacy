import discord
import contextlib
import itertools
from datetime import datetime, timedelta
from .resources import points, tiers, Queues
from utils.formats import format_dt, format_relative
from typing import Union, Dict, List, Any, Optional, Tuple

# if TYPE_CHECKING:
from .useful import calculate_level_xp, iso_to_time, GetFormat, JSON
from .resources import get_emoji_tier

class Embed(discord.Embed): # Custom Embed
    def __init__(self, description:str = None, color: Union[discord.Color, int] = 0xfd4554, **kwargs: Any) -> discord.Embed:
        super().__init__(description=description, color=color, **kwargs)

class Generate_Embed:

    def death_match(match: Dict, endpoint: Any) -> List[discord.Embed]:

        result = GetFormat.death_match(match, endpoint)
        color = result['color']
        highest = result['highest']
        second = result['second']
        your_kill = result['your_kill']
        match_result = result['match_result']
        playdate = result['playdate']
        gamelength = result['gamelength']
        queue_id = result['queue_id']
        queue_emoji = result['queue_emoji']
        your_name = result['your_name']
        your_agent = result['your_agent']
        match_result_text = result['match_result']

        players = result['players']
        player_score = result['player_score']
        player_kda = result['player_kda']
        player_rank = result['player_rank']
        player_agents = result['player_agents']

        footer = {"text": f"{match_result_text}"}
        author = {"name": f"{your_name} - {queue_id.capitalize()}", "icon_url": your_agent['icon']['icon']}

        embed = discord.Embed(color=color)
        embed.set_author(**author)
        embed.add_field(name='Player', value='\n'.join([' '.join(x) for x in itertools.zip_longest(player_agents, player_rank, players)]))
        embed.add_field(name='SCORE', value='\n'.join(player_score))
        embed.add_field(name='KDA', value='\n'.join(player_kda))
        embed.set_footer(**footer)
        
        embed_c = discord.Embed(color=color)
        embed_c.set_author(**author)
        embed_c.set_footer(**footer)
        for member, score, kda, rank, agent in zip(players, player_score, player_kda, player_rank, player_agents):
            embed_c.add_field(name=f"{agent}{rank} {member}", value=f'Score: {score}\nKDA: {kda}')

        
        return [embed], [embed_c]

    def match_result(puuid, match_result: str, queue_id:str, endpoint: Any) -> List[discord.Embed]:
        
        match_details = GetFormat.match_details(puuid, match_result)

        if queue_id == "deathmatch":
            return Generate_Embed.death_match(match_details, endpoint)
        
        result = GetFormat.match_result(match_details, endpoint)
        return Generate_Embed.build_match(result)

    def build_match(result: Dict) -> Tuple[List[discord.Embed], List[discord.Embed]]:

        color = result['color']
        match_score = result['match_score']
        playdate = result['playdate']
        playtime = result['playtime']
        match_result_text = result['match_result']
        gamelength = result['gamelength']
        queue_id = result['queue_id']
        map_name = result['map']
        queue_emoji = result['queue_emoji']
        timelines = result['timelines']
        your_name = result['your_name']
        your_abilities = result['your_abilities']
        your_agent = result['your_agent']

        team_a = result['team_a']
        team_b = result['team_b']
        opponent = result['opponent']
        opponent_kda = result['opponent_kda']

        footer = {"text": f"{match_result_text}"}
        author = {"name": f"{your_name} - {Queues[queue_id]['name']}", "icon_url": your_agent['icon']['icon']}
        # footer = {"text": f"{gamelength} • {queue_id.capitalize()}"}
        # footer = {"text": f"{playtime} • {queue_id.capitalize()} • {gamelength}"}
        timestamp = datetime.fromtimestamp(playdate)

        # TEAM A
        embed = discord.Embed(color=color, timestamp=timestamp) 
        # embed.set_author(name=f'{queue_emoji} {map_name} {match_score}')
        embed.set_author(**author)
        embed.title =  f'{queue_emoji} {map_name} - {match_score}'
        embed.add_field(name='TEAM A', value='\n'.join(team_a['player']))
        embed.add_field(name='ACS', value='\n'.join(team_a['acs']))
        embed.add_field(name='KDA', value='\n'.join(team_a['kda']))

        # TEAM B
        embed.add_field(name='TEAM B', value='\n'.join(team_b['player']))
        embed.add_field(name='ACS', value='\n'.join(team_b['acs']))
        embed.add_field(name='KDA', value='\n'.join(team_b['kda']))

        if len(timelines) > 24:
            embed.add_field(name='Timeline:', value=''.join(timelines[:24]), inline=False)
            embed.add_field(name=''.join(timelines[24:]), value='\u200b', inline=False)
        else:
            embed.add_field(name='Timeline:', value=''.join(timelines), inline=False)
        embed.set_footer(**footer)

        # ------ PAGE 2 ------ #
        
        embed2 = discord.Embed(color=color, timestamp=timestamp)
        embed2.title = f'{queue_emoji} {map_name} - {match_score}'
        embed2.set_author(**author)
        # embed2.set_author(name=f'{queue_emoji} {map_name} {match_score}')
        embed2.set_footer(**footer)
        
        # TEAM A
        embed2.add_field(name='TEAM A', value='\n'.join(team_a['player']))
        embed2.add_field(name='FK', value='\n'.join(team_a['first_blood']))
        embed2.add_field(name='HS%', value='\n'.join(team_a['hs_percent']))
       
        # TEAM B
        embed2.add_field(name='TEAM B', value='\n'.join(team_b['player']))
        embed2.add_field(name='FK', value='\n'.join(team_b['first_blood']))
        embed2.add_field(name='HS%', value='\n'.join(team_b['hs_percent']))
        
        # ------ PAGE 3 ------ #

        embed3 = discord.Embed(color=color, timestamp=timestamp)
        embed3.title = f'{your_name} - Performance'
        # embed3.set_author(name=f'{queue_emoji} {your_name} - Performance')
        embed3.add_field(name='KDA', value='\n'.join(opponent_kda))
        embed3.add_field(name='Opponent', value='\n'.join(opponent))
        embed3.add_field(name='Abilties', value=your_abilities, inline=False)
        embed3.set_footer(**footer)

        # embed mobile 
        
        embed_mb = discord.Embed(color=color, timestamp=timestamp)
        embed_mb.set_author(**author)
        embed_mb.add_field(name='\u200b', value='**TEAM A**')
        for player, acs, kda in zip(team_a['player'], team_a['acs'], team_a['kda']):
            embed_mb.add_field(name=player, value=f'ACS: {acs}\nKDA: {kda}', inline=False)
        embed_mb.add_field(name='\u200b', value='**TEAM B**')
        for player, acs, kda in zip(team_b['player'], team_b['acs'], team_b['kda']):
            embed_mb.add_field(name=player, value=f'ACS: {acs}\nKDA: {kda}', inline=False)
        
        if len(timelines) >= 24:
            embed_mb.add_field(name='Timeline:', value=''.join(timelines[:24]), inline=False)
            embed_mb.add_field(name=''.join(timelines[24:]), value='\u200b', inline=False)
        else:
            embed_mb.add_field(name='Timeline:', value=''.join(timelines), inline=False)

        # compact embed page 2
        embed_mb2 = discord.Embed(color=color, timestamp=timestamp)
        embed_mb2.set_author(**author)
        embed_mb2.add_field(name='\u200b', value='**TEAM A**')
        for player, fb, hs in zip(team_a['player'], team_a['first_blood'], team_a['hs_percent']):
            embed_mb2.add_field(name=player, value=f'First Bloods: {fb}\nHeadshot%: {hs}', inline=False)
        embed_mb2.add_field(name='\u200b', value='**TEAM B**')
        for player, fb, hs in zip(team_b['player'], team_b['first_blood'], team_b['hs_percent']):
            embed_mb2.add_field(name=player, value=f'First Bloods: {fb}\nHeadshot%: {hs}', inline=False)

        # compact embed page 3
        embed_mb3 = discord.Embed(color=color, timestamp=timestamp)
        embed_mb3.set_author(name=f'{your_name} - Performance', icon_url=your_agent['icon']['icon'])
        embed_mb3.add_field(name='KDA Opponent', value='\n'.join([' '.join(x) for x in itertools.zip_longest(opponent_kda, opponent)]))
        embed_mb3.add_field(name='Abilties', value=your_abilities, inline=False)

        embeds = []
        embeds_mb = []
        embeds.append(embed)
        embeds.append(embed2)      
        embeds_mb.append(embed_mb)
        embeds_mb.append(embed_mb2)
        if queue_id not in ['ggteam']:
            embeds.append(embed3)
            embeds_mb.append(embed_mb3)
        
        return embeds, embeds_mb

    def __giorgio_embed(skin: Dict) -> discord.Embed:
        uuid, name, price, icon = skin['uuid'], skin['name'], skin['price'], skin['icon']

        embed = Embed(f"{get_emoji_tier(uuid)} **{name}**\n{points['vp']} {price}", color=0x0F1923)
        embed.set_thumbnail(url=icon)
        return embed

    @classmethod
    def store(cls, player: str, offer: Dict, language: str, response: Dict) -> List[discord.Embed]:
        
        data = GetFormat.offer(offer, language)

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

        data = GetFormat.mission(mission, language)

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

        BTP = GetFormat.battlepass(data, season, language)

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

        night_mk = GetFormat.nightmarket(offer, language, response)
        
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