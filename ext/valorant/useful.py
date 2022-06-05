from __future__ import annotations

import json
import os
import contextlib
from typing import Tuple, Dict, List, Any, Optional, TYPE_CHECKING
from datetime import datetime
from utils.formats import deltaconv

if TYPE_CHECKING:
    from .api import VALORANT_ENDPOINT as Endpoint

current_season = '3e47230a-463c-a301-eb7d-67bb60357d4f'

def percent(*args: Optional[List[int]]) -> Optional[List]: 
    t = sum(args) 
    return [100 * y / t for y in args] 

# ---------- TIME UTILS ---------- #

def calculate_level_xp(level: int) -> int:
    '''Calculate level xp'''

    level_multiplier = 750
    if level >= 2 and level <= 50:
        return 2000 + (level - 2) * level_multiplier
    elif level >= 51 and level <= 55:
        return 36500
    else:
        return 0

# ---------- JSON LOADER ---------- #

class JSON:

    def create(filename: str, formats: Dict) -> None:
        '''Create json file'''
        file_path =  f"ext/valorant/data/"+ filename +".json"
        file_dir = os.path.dirname(file_path)
        os.makedirs(file_dir, exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w") as fp:
                json.dump(formats, fp, indent=2)

    @classmethod
    def ext_read(cls, filename: str, force=True) -> Dict:
        '''Read json file'''
        try:
            with open("ext/valorant/ext_data/" + filename + ".json", "r", encoding='utf-8') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            if force:
                cls.create(filename, {})
                return cls.read(filename, force=False)
        return data


    @classmethod
    def read(cls, filename: str, force=True) -> Dict:
        '''Read json file'''
        try:
            with open("ext/valorant/data/" + filename + ".json", "r", encoding='utf-8') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            if force:
                cls.create(filename, {})
                return cls.read(filename, force=False)
        return data

    @classmethod
    def save(cls, filename: str, data: Dict) -> None:
        '''Save data to json file'''
        try:
            with open("ext/valorant/data/" + filename + ".json", 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, indent=2, ensure_ascii=False)
        except FileNotFoundError:
            cls.create(filename, {})
            return cls.save(filename, data)

# ---------- GET DATA ---------- #

class GetData:

    def cache() -> Dict:
        """Get cache from data"""
        return JSON.read('cache')

    @classmethod
    def agent(cls, uuid: str = None) -> Dict:
        """Get agent data"""
        data = JSON.ext_read('agents')
        if uuid is None:
            return data['agents']
        return data['agents'][uuid]

class GetItem:
    
    # def __init__(self, language: str=None):
    #     self.language = language
    #     self.read_cache()

    # def read_cache(self) -> None:
    #     '''Read cache'''
    #     data = data_read('cache')
    #     self.skins = data["skins"]
    #     self.sprays = data["sprays"]
    #     self.titles = data["titles"]
    #     self.playercards = data["playercards"]
    #     self.buddies = data["buddies"]
    #     self.contracts = data["contracts"]
    #     self.prices = data["prices"]
    #     self.chromas = data["chromas"]
    #     self.tiers = data["tiers"]

    def get_type_name(uuid: str) -> str:
        '''Get item type'''
        from .resources import get_item_type
        return get_item_type(uuid)
    
    @classmethod
    def Get_by_type(cls, item_type:str, item_uuid:str = None) -> Dict:
        from .resources import get_item_type
        
        if '-' in item_type:
            item_type = get_item_type(item_type) 
        
        if item_type == 'Agents':
            return cls.get_agent(item_uuid)
        elif item_type == 'Contracts':
            return cls.get_contract(item_uuid)
        elif item_type in ['Sprays', 'Spray']:
            return cls.get_spray(item_uuid)
        elif item_type in ['Gun Buddies', 'EquippableCharmLevel']:
            return cls.get_buddie(item_uuid)
        elif item_type in ['Player Cards', 'PlayerCard']:
            return cls.get_playercard(item_uuid)
        elif item_type in ['Skins', 'EquippableSkinLevel']:
            return cls.get_skin(item_uuid)
        elif item_type == 'Skins chroma':
            ...
        elif item_type in ['Player titles', 'Title']:
            return cls.get_title(item_uuid)
        elif item_type == 'Currency':
            return cls.get_currency(item_uuid)

    async def get_agent(uuid: str, force: bool =True) -> Dict:
        '''Get agent data'''
        try:
            data = JSON.read('agents')
            agent = data[uuid]
        except KeyError:
            if force:
                from .cache import fetch_agent
                fetch_agent()
                return GetItem.get_agent(uuid, False)
            agent = {}
        return agent
    
    def get_skin(uuid: str, force: bool =True) -> Dict:
        '''Get Skin data'''
        skin = None
        try:
            skindata = JSON.read('cache')
            skin = skindata["skins"][uuid]
        except KeyError:
            if force:
                from .cache import fetch_skin
                fetch_skin()
                return GetItem.get_skin(uuid, False)
        return skin

    def get_skin_price(uuid: str) -> str:
        '''Get Skin price by skin uuid'''
        try:
            skin = JSON.read('cache')
            cost = skin["prices"][uuid]
        except KeyError:
            cost = '-'
        return cost

    @classmethod
    def get_skin_tier_icon(cls, uuid: str, force: bool =True) -> str:
        '''Get Skin skin tier image'''
        
        skin = cls.get_skin(uuid)
        tier_uuid = skin["tier"]
        icon = None
        try:
            data = JSON.read('cache')
            tier = data["tiers"][tier_uuid]
            icon = tier["icon"]
        except KeyError:
            if force:
                from .cache import fetch_tier
                fetch_tier()
                return GetItem.get_skin_tier_icon(uuid, False)
        return icon

    @classmethod
    def get_skin_name(cls, uuid: str, language:str) -> str:
        '''Get Skin name'''
        skin = cls.get_skin(uuid)
        name = skin['names'][language]
        return name

    @classmethod
    def get_skin_icon(cls, uuid: str) -> str:
        '''Get Skin icon'''
        skin = cls.get_skin(uuid)
        icon = skin['icon']
        return icon

    def get_contract(uuid: str, force: bool=True) -> str:
        '''Get Contracts'''
        contract = None
        try:
            data = JSON.read('contracts') 
            contract = data["contracts"][uuid]
        except KeyError:
            if force:
                from .cache import fetch_contracts
                fetch_contracts()
                return GetItem.get_contract(uuid, False)
        return contract

    def get_spray(uuid: str, force=True) -> Dict:
        """Get Spray"""
        spray = None
        try:
            data = JSON.read('cache')
            spray = data["sprays"][uuid]  
        except KeyError:
            if force:
                from .cache import fetch_spray
                fetch_spray()
                return GetItem.get_spray(uuid, force=False)
        return spray

    def get_title(uuid: str, force=True) -> Dict:
        """Get Title"""
        title = None
        try:
            data = JSON.read('cache')
            title = data["titles"][uuid]
        except KeyError:
            if force:
                from .cache import fetch_playertitles
                fetch_playertitles()
                return GetItem.get_title(uuid, False)
        return title

    def get_playercard(uuid: str, force=True) -> Dict:
        """Get Playercard"""
        card = None
        try:
            data = JSON.read('cache')
            card = data["playercards"][uuid]
        except KeyError:
            if force:
                from .cache import fetch_playercard
                fetch_playercard()
                return GetItem.get_playercard(uuid, False)
        return card

    def get_buddie(uuid: str, force: bool =True) -> Dict:
        """Get Buddie"""
        buddie = None
        try:
            data = JSON.read('cache')
            buddie = data["buddies"][uuid]
        except KeyError:
            if force:
                from .cache import fetch_buddies
                fetch_buddies()
                return GetItem.get_buddie(uuid, False)
        return buddie

    def get_currency(uuid: str, force: bool=True) -> Dict:
        """Get Currency"""
        currency = None
        try:
            data = JSON.read('cache')
            currency = data["currencies"][uuid]    
        except KeyError:
            if force:
                from .cache import fetch_currencies
                fetch_currencies()
                return GetItem.get_currency(uuid, False) 
        return currency

    def get_bundle(uuid: str, force: bool=True) -> Dict:
        bundle = None
        try:
            data = JSON.read('cache')
            bundle = data["bundles"][uuid]
        except KeyError:
            if force:
                from .cache import fetch_bundles
                fetch_bundles()
                return GetItem.get_bundle(uuid)
        return bundle

    # future contetnt

    def get_skin_chromas(uuid: str, force: bool=True) -> Dict:
        data = JSON.read('skinchromas')
        chroma = None
        try:
            chroma = data["chromas"][uuid]
        except KeyError:
            if force:
                from .cache import fetch_skinchromas
                fetch_skinchromas()
                return GetItem.get_skin_chromas(uuid, False)
        return chroma

    def get_skin_lvl_or_name(name: str, uuid: str, language: str) -> Dict:
        """Get Skin uuid by name"""
        data = JSON.read('cache')
        skin = None
        with contextlib.suppress(Exception):
            skin = data["skins"][uuid]
        with contextlib.suppress(Exception):
            if skin is None:
                skin = [data["skins"][x] for x in data["skins"] if data["skins"][x]['names'][language] in name][0]
        return skin

    def spray_slot(slot_id: str) -> int:
        from .resources import spray_slots
        return spray_slots[slot_id]

class GetFormat:

    def offer(data: Dict, language: str) -> Dict:
        '''Get skins format'''

        offer_list = data["SkinsPanelLayout"]["SingleItemOffers"]
        duration = data["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]

        skin_count = 0
        skin_source = {}
        
        for uuid in offer_list:
            skin = GetItem.get_skin(uuid)
            price = GetItem.get_skin_price(uuid)
            tier_icon = GetItem.get_skin_tier_icon(uuid)
            name, icon = skin['names']['en-US'], skin['icon']

            if skin_count == 0:
                skin1 = dict(name=name, icon=icon, price=price, tier=tier_icon, uuid=uuid)
            elif skin_count == 1:
                skin2 = dict(name=name, icon=icon, price=price, tier=tier_icon, uuid=uuid)
            elif skin_count == 2:
                skin3 = dict(name=name, icon=icon, price=price, tier=tier_icon, uuid=uuid)
            elif skin_count == 3:
                skin4 = dict(name=name, icon=icon, price=price, tier=tier_icon, uuid=uuid)
            skin_count += 1

        skin_source = {
            'skin1': skin1,
            'skin2': skin2,
            'skin3': skin3,
            'skin4': skin4,
            'duration': duration
        }
        return skin_source

    def nightmarket(offer: Dict, language: str, response: Dict) -> Dict:
        '''Get Nightmarket format'''
        
        try:
            night_offer = offer['BonusStore']['BonusStoreOffers']
        except KeyError:
            raise RuntimeError(response.get('NIGMARKET_HAS_END'))
        duration = offer['BonusStore']['BonusStoreRemainingDurationInSeconds']

        night_market = {}
        count = 0
        for offer in night_offer:
            count += 1
            price = *offer['Offer']['Cost'].values(),
            Disprice = *offer['DiscountCosts'].values(),
            
            uuid = offer['Offer']['OfferID']
            skin = GetItem.get_skin(uuid)
            name = skin['names'][language]
            icon = skin['icon']
            tier = GetItem.get_skin_tier_icon(uuid)
            
            night_market['skin' + f'{count}'] = {
                'uuid': uuid,
                'name': name,
                'tier': tier,
                'icon': icon,
                'price': price[0],
                'disprice': Disprice[0]
            }
        data = {
            'nightmarket': night_market,
            'duration': duration
        }
        return data

    def mission(data: Dict, language:str) -> Dict[str, str]:
        '''Get mission format'''

        mission = data["Missions"]

        weekly = []
        daily = []
        newplayer = []
        daily_end = ''
        try:
            weekly_end = data['MissionMetadata']['WeeklyRefillTime']
        except KeyError:
            weekly_end = ''

        def get_mission_by_id(ID):
            try:
                data = JSON.read('missions')
                mission = data['missions'][ID]
            except KeyError:
                from .cache import fetch_mission
                fetch_mission()
                return get_mission_by_id(ID)
            return mission
        
        for m in mission:
            mission = get_mission_by_id(m['ID'])
            *complete, = m['Objectives'].values()
            title = mission['titles'][language]
            progress = mission['progress']
            xp = mission['xp']


            format_m = f"\n{title} | **+ {xp:,} XP**\n- **`{complete[0]}/{progress}`**"
            
            if complete[0] != progress:
                if mission['type'] == 'EAresMissionType::Weekly':
                    weekly.append(format_m)
                if mission['type'] == 'EAresMissionType::Daily':
                    daily_end = m['ExpirationTime']
                    daily.append(format_m)
                if mission['type'] == 'EAresMissionType::NPE':
                    newplayer.append(format_m)

        misson_data = dict(daily=daily, weekly=weekly, daily_end=daily_end, weekly_end=weekly_end, newplayer=newplayer)
        return misson_data
        
    def leaderboard(data: Dict) -> List[str]:
        from .resources import ranks

        entries = []

        for entry in data:
            ranktier = entry["competitiveTier"]
            name = entry["gameName"]
            tag = entry["tagLine"]
            rating = entry["rankedRating"]
            index = entry["leaderboardRank"]
            won = entry["numberOfWins"]
            is_private = entry["IsAnonymized"]

            if is_private:
                player_name = 'Secret Agent'
            else:
                player_name = name + '#' + tag

            entries.append(f"{index}. {ranks[str(ranktier)]['emoji']} {player_name} - {rating}")

        return entries
    
    @classmethod
    def battlepass(cls, data: Dict, season: str, language: str) -> Dict:
        
        data = data['Contracts']
        contracts = JSON.read('contracts')
        # data_contracts['contracts'].pop('version')

        season_id = season['id']
        season_end = season['end']

        btp = cls.__get_contracts_by_season_id(data, contracts, season_id, language)
        
        if not btp: raise RuntimeError(f"Failed to get battlepass")

        tier, act, xp, reward = btp['tier'], btp['act'], btp['xp'], btp['reward']
        
        # #testing
        # data = JSON.read('item')
        # tier = int(data.get('tier'))

        item_reward = GetFormat.__get_contract_tier_reward(tier, reward)
        
        reward_type, reward_uuid = item_reward['type'], item_reward['uuid']

        # item = cls.__get_item_battlepass(reward_type, reward_uuid, language)
        item = GetItem.Get_by_type(reward_type, reward_uuid)

        name = item['names'][language]
        overite_type = {
            'Currency': 'Points',
            'EquippableSkinLevel': 'Skin',
            'EquippableCharmLevel': 'Buddie'
        }
        type = overite_type.get(reward_type, reward_type)

        try:
            icon = item['icon']['wide']
        except TypeError:
            icon = item.get('icon', False)

        return dict(data=dict(tier=tier, act=act, xp=xp, reward=name, type=type, icon=icon, end=season_end))


    def __get_contracts_by_season_id(contracts: Dict, data_contracts: Dict, season_id: str, language: str) -> Dict:
        '''Get battlepass info'''

        try:
            contracts_uuid = [x for x in data_contracts['contracts'] if data_contracts['contracts'][x]['reward']['relationUuid'] == season_id]
        except KeyError:
            from .cache import fetch_contracts
            fetch_contracts()
            return GetFormat.__get_contracts_by_season_id(contracts, JSON.read('contracts'), season_id, language)
        
        if len(contracts_uuid) == 0:
            return dict(success=False)

        battlepass = [x for x in contracts if x['ContractDefinitionID'] == contracts_uuid[0]]
        TIER = battlepass[0]['ProgressionLevelReached']  
        XP = battlepass[0]['ProgressionTowardsNextLevel']
        REWARD = data_contracts['contracts'][contracts_uuid[0]]['reward']['chapters']
        ACT = data_contracts['contracts'][contracts_uuid[0]]['names'][language]

        return dict(success=True, tier=TIER, act=ACT, xp=XP, reward=REWARD)
    
    def __get_contract_tier_reward(tier: int, reward: List[Dict]) -> Dict:
        '''Get tier reward'''

        data = {}
        count = 0

        for lvl in reward:
            for rw in lvl["levels"]:
                count += 1
                data[count] = rw['reward']
        
        next_reward = tier + 1
        if tier == 55: next_reward = 55
        current_reward = data[next_reward]

        return current_reward

    def inventory(data: Dict) -> List[str]:
        
        language = 'en-US'

        from .resources import weapon_ids

        loadout = {'weapons': [], 'sprays': [], 'playercard': {}, 'playertitle': {}}
        
        def loadout_format(weapon_id: str, uuid: str, SkinLevelID: str) -> Tuple[str, str, str]:
            from ext.valorant.resources import tiers as TIERS

            skin = GetItem.get_skin_chromas(uuid)
            weapon = weapon_ids[weapon_id]['name']
            weapon_type = weapon_ids[weapon_id]['type']
            name = skin['names'][language]
            icon = skin['icon']
            if 'Level' in name: name = name.split('Level')[0]
            if '(Variant' in name: name = name.split('(Variant')[0]
            if icon is None or name == weapon: icon = skin['full_render']
            
            color, emoji = 0x0F1923, ''

            skin = GetItem.get_skin_lvl_or_name(name, SkinLevelID, language)
            
            try:
                tier = skin['tier']
                tier_color = TIERS[tier]['color']
                emoji = TIERS[tier]['emoji']
                color = tier_color
            except (KeyError, TypeError):
                pass

            return weapon, name, icon, color, emoji, weapon_type

        for weapon in data['Guns']:
            weapon, name, icon, color, emoji, weapon_type = loadout_format(weapon['ID'], weapon['ChromaID'], weapon['SkinLevelID'])
            loadout['weapons'].append({
                'weapon': weapon,
                'name': name,
                'icon': icon,
                'color': color,
                'emoji': emoji,
                'type': weapon_type
            })
        
        for item in data['Sprays']:
            spray = GetItem.get_spray(item['SprayID'])
            name = spray['names'][language]
            icon = spray['icon']
            slot = GetItem.spray_slot(item['EquipSlotID'])
            loadout['sprays'].append({'name': name, 'icon': icon, 'slot': slot})
        
        loadout['playercard'] = GetItem.get_playercard(data['Identity']['PlayerCardID'])
        loadout['playertitle'] = GetItem.get_title(data['Identity']['PlayerTitleID'])

        # for skin in skins_inventory["Entitlements"]:
        #     print(get_skin_name(skin['ItemID']))
        #     print(skin['ItemID'])

        return loadout

    def death_match(match: Dict, endpoint: Endpoint) -> Dict:
        """Get death match data"""

        from .resources import Queues, RANKS, maps as Maps

        AgentsData = GetData.agent()

        puuid = match['your_puuid']
        map_id = match['MapID']
        map_name = Maps[map_id]
        playdate = match['playdate']
        gamelength = deltaconv(match['gamelength'] / 1000 / 60)
        queueID = match['queueID']
        your_agent = AgentsData[match['your_agent']]
        your_name = match['your_name']
        player_won = match['won']

        color = 0x60dcc4 if puuid == player_won else 0xfc5c5c
        result_text = 'VICTORY' if puuid == player_won else 'DEFEAT'
        queue_emoji = Queues[queueID]['emoji'] if queueID in Queues else Queues['unrated']['emoji']

        players = []
        player_score = []
        player_kda = []
        player_rank = []
        player_agents = []

        highest_kill = 0
        your_kill = 0
        second_kill = 0

        AgentsData = GetData.agent()
        for index, player in enumerate(sorted(match['player'].values(), key=lambda x: x['stats']['score'], reverse=True), start=1):
            
            locale_code = 'en-US'
            player_puuid = player['puuid']

            mmr = endpoint.fetch_player_mmr(player_puuid)
            try:
                rank = mmr['QueueSkills']['competitive']['SeasonalInfoBySeasonID'][current_season]['Rank']
            except (TypeError, KeyError):
                rank = 0

            stats = player['stats']
            kill = stats['kills']
            death = stats['deaths']
            assist = stats['assists']
            score = stats['score']
            agent_uuid = player['agent_uuid']
            rank_emoji = RANKS[str(rank)]['emoji']
            player_name = player['player'] if player['player'] != your_name else f'**{player["player"]}**'

            player_agent = AgentsData[agent_uuid]
            AgentEmoji = player_agent['emoji']

            # label = f"{AgentEmoji} {rank_emoji} {player_name}"
            SCORE = f"{int(score)}"
            KDA = f"{kill}/{death}/{assist}"
            if index == 1:
                highest_kill = kill
                SCORE += ' <:TX_Icon_MVPStar:973844286552543242>'
            if index == 2:
                second_kill = kill

            if player_puuid == puuid:
                your_kill = kill

            players.append(player_name)
            player_agents.append(AgentEmoji)
            player_rank.append(rank_emoji)
            player_score.append(SCORE)
            player_kda.append(KDA)

        return dict(
            map=map_name,
            highest=highest_kill,
            second=second_kill,
            your_kill=your_kill,
            match_result=result_text,
            playdate=playdate,
            gamelength=gamelength,
            queue_id=queueID,
            queue_emoji=queue_emoji,
            your_name=your_name,
            your_agent=your_agent,
            color=color,
            players=players,
            player_score=player_score,
            player_kda=player_kda,
            player_rank=player_rank,
            player_agents=player_agents
        )

    def match_result(match: Dict, endpoint: Any) -> Dict:
        from .resources import Queues, RANKS, maps as Maps
            
        map_id = match['MapID']
        map_name = Maps[map_id]
        playdate = match['playdate']
        playdatetime = (datetime.fromtimestamp(playdate)).strftime('%#d %b %Y')
        gamelength = deltaconv(match['gamelength'] / 1000 / 60)
        queueID = match['queueID']
        your_team = match['your_team']
        your_agent = match['your_agent']
        your_rank = match['your_rank']
        your_KDA = match['your_KDA']
        your_name = match['your_name']
        won = match['won']
        winner_score = match['winner_score']
        loser_score = match['loser_score']
        match_score = f'{winner_score}:{loser_score}' if your_team == won else f'{loser_score}:{winner_score}'
        color = 0x60dcc4 if your_team == won else 0xfc5c5c
        result_text = 'VICTORY' if your_team == won else 'DEFEAT'
        timelines = match['timelines']
        queue_emoji = Queues[queueID]['emoji'] if queueID in Queues else Queues['unrated']['emoji']

        your_abilities = ''
        your_agent = {}

        # TEAM A
        TEAM_A_Player = []
        TEAM_A_RANK = []
        TEAM_A_ACS = []
        TEAM_A_KDA = []
        TEAM_A_HS_PERCENT = []
        TEAM_A_KILL_DEL_DEATH = []
        TEAM_A_FIRST_BLOOD = []

        # TEAM B
        TEAM_B_Player = []
        TEAM_B_RANK = []
        TEAM_B_ACS = []
        TEAM_B_KDA = []
        TEAM_B_HS_PERCENT = []
        TEAM_B_KILL_DEL_DEATH = []
        TEAM_B_FIRST_BLOOD = []
        
        OPPONENT = []
        OPPONENT_KDA = []

        AgentsData = GetData.agent()
        for index, player in enumerate(sorted(match['player'].values(), key=lambda x: x['stats']['score'], reverse=True), start=1):

            locale_code = 'en-US'
            puuid = player['puuid']
            stats = player['stats']
            damage = stats['damage']
            ability = stats['ability']
            kill = stats['kills']
            death = stats['deaths']
            assist = stats['assists']
            score = stats['score']
            rounds = stats['rounds']

            agent_uuid = player['agent_uuid']
            headshot = damage['headshots']
            bodyshot = damage['bodyshots']
            legshot = damage['legshots']
            first_blood = stats['firstkills']
            player_name = player['player'] if player['player'] != your_name else f'**{player["player"]}**'
            
            rank = player['rank_tier']
            if queueID == 'custom':
                mmr = endpoint.fetch_player_mmr(puuid)
                try:
                    rank = mmr['QueueSkills']['competitive']['SeasonalInfoBySeasonID'][current_season]['Rank']
                except (TypeError):
                    rank = rank

            rank_emoji = RANKS[str(rank)]['emoji']
            player_agent = AgentsData[agent_uuid]
            AgentName = player_agent['names'][locale_code]
            AgentEmoji = player_agent['emoji']

            label = f"{AgentEmoji} {rank_emoji} {player_name}"

            FK = f"{first_blood}"
            ACS = f"{int(score / rounds)}"
            KDA = f"{kill}/{death}/{assist}"
            if index == 1: ACS += ' <:TX_Icon_MVPStar:973844286552543242>'

            try:
                HS_Percent, BS_Percent, LEG_percent = percent(headshot, bodyshot, legshot)
            except ZeroDivisionError:
                HS_Percent, BS_Percent, LEG_percent = 0, 0, 0

            kill_del_death = f'{kill - death}'

            if player['team'] == "Blue":
                TEAM_A_Player.append(label)
                TEAM_A_RANK.append(rank_emoji)
                TEAM_A_ACS.append(ACS)
                TEAM_A_KDA.append(KDA)
                TEAM_A_HS_PERCENT.append(f'{HS_Percent:.1f}%')
                TEAM_A_KILL_DEL_DEATH.append(kill_del_death)
                TEAM_A_FIRST_BLOOD.append(FK)
            elif player['team'] == "Red":
                TEAM_B_Player.append(label)
                TEAM_B_RANK.append(rank_emoji)
                TEAM_B_ACS.append(ACS)
                TEAM_B_KDA.append(KDA)
                TEAM_B_HS_PERCENT.append(f'{HS_Percent:.1f}%')
                TEAM_B_KILL_DEL_DEATH.append(kill_del_death)
                TEAM_B_FIRST_BLOOD.append(FK)

            if your_team != player['team']:
                OPPONENT.append(label)
                OPPONENT_KDA.append('0 / 0 / 0')

            if your_name == player['player']:
                
                your_agent = player_agent

                if not queueID in ['ggteam', 'deathmatch']:

                    # player
                    p_grenade = round(ability['grenade'] / rounds, 1)
                    p_ability1 = round(ability['ability1'] / rounds, 1)
                    p_ability2 = round(ability['ability2'] / rounds, 1)
                    p_ultimate = round(ability['ultimate'] / rounds, 1)

                    # agent abilities emoji
                    emoji_grenade = player_agent['abilities']['Grenade']['emoji']
                    emoji_ability1 = player_agent['abilities']['Ability1']['emoji']
                    emoji_ability2 = player_agent['abilities']['Ability2']['emoji']
                    emoji_ultimate = player_agent['abilities']['Ultimate']['emoji']

                    your_abilities = f'{emoji_grenade} {p_grenade} {emoji_ability1} {p_ability1} {emoji_ability2} {p_ability2} {emoji_ultimate} {p_ultimate}'

        return dict(
            map_id=map_id,
            map=map_name,
            match_score=match_score,
            match_result=result_text,
            won=won,
            winner_score=winner_score,
            loser_score=loser_score,
            playdate=playdate,
            playtime=playdatetime,
            gamelength=gamelength,
            queue_id=queueID,
            queue_emoji=queue_emoji,
            your_name=your_name,
            your_abilities=your_abilities,
            your_agent=your_agent,
            your_team=your_team,
            your_rank=your_rank,
            your_KDA=your_KDA,
            color=color,
            timelines=timelines,
            opponent=OPPONENT,
            opponent_kda=OPPONENT_KDA,
            team_a=dict(
                player=TEAM_A_Player,
                rank=TEAM_A_RANK,
                acs=TEAM_A_ACS,
                kda=TEAM_A_KDA,
                hs_percent=TEAM_A_HS_PERCENT,
                kill_del_death=TEAM_A_KILL_DEL_DEATH,
                first_blood=TEAM_A_FIRST_BLOOD
            ),
            team_b=dict(
                player=TEAM_B_Player,
                rank=TEAM_B_RANK,
                acs=TEAM_B_ACS,
                kda=TEAM_B_KDA,
                hs_percent=TEAM_B_HS_PERCENT,
                kill_del_death=TEAM_B_KILL_DEL_DEATH,
                first_blood=TEAM_B_FIRST_BLOOD
            )
        )

    def match_details(puuid:str, match_details: Dict) -> str:
        """ the match details """

        from .resources import EmojiResult


        JSON.save('match_details', match_details)

        matchInfo = match_details['matchInfo']

        matchId = matchInfo['matchId']
        MapId = matchInfo['mapId']
        gameLengthMillis = matchInfo['gameLengthMillis']
        playdate = matchInfo['gameStartMillis'] / 1000
        queueID = matchInfo['queueID']
        seasonId = matchInfo['seasonId']

        if matchInfo['provisioningFlowID'] == 'CustomGame':
            queueID = 'custom'

        # match_details

        # score
        winner = ''
        winner_score = 0
        loser = ''
        loser_score = 0
        teams = match_details['teams']
        for team in teams:
            if team['won'] is True:
                winner = team['teamId']
                winner_score = team['roundsWon']
            else:
                loser = team['teamId']
                loser_score = team['roundsWon']

        matcah_results = {}
        player_stats = {}
        blueteam_uuid = []
        redteam_uuid = []

        your_team = ''
        your_agent = ''
        your_rank = 0
        your_KDA = ''

        blue_loadout = 0
        blue_spent = 0
        blue_remaining = 0

        red_loadout = 0
        red_spent = 0
        red_remaining = 0   
        
        # builds_stats 
        for player in match_details['players']:
            player_subject = player['subject']
            player_stats[player_subject] = {
                'puuid': player_subject,
                'team': '',
                'player': '',
                # 'agent': get_agent(player['characterId']),
                'agent_uuid': '',
                'rank_tier': '',
                'playercard_uuid': '',
                'title_uuid': '',
                'level': '',
                'stats': {
                    'kills': 0,
                    'deaths': 0,
                    'assists': 0,
                    'score': 0,
                    'rounds': 0,
                    'loadoutValue': 0,
                    'firstkills': 0,
                    'firstdeaths': 0,
                    'spent': 0,
                    'multikills': 0,
                    'plants': 0,
                    'defuses': 0,
                    'playtimeMillis': 0,
                    'ability' : {},
                    'damage': {
                        'total': 0,
                        'headshots': 0,
                        'bodyshots': 0,
                        'legshots': 0,
                    }
                }
            }

        for player in match_details['players']:
            player_subject = player['subject']
        
            player_team_id = player['teamId']
            if player_team_id == 'Blue':
                blueteam_uuid.append(player_subject)
            else:
                redteam_uuid.append(player_subject)

            player_stats_insert = player_stats[player_subject]

            stats = player['stats']
            abilityCasts = stats.get('abilityCasts', None)

            # insert player stats
            agent_uuid = player['characterId']
            player_team_id = player['teamId']
            player_competitiveTier = player['competitiveTier']
            player_card = player['playerCard']
            player_title = player['playerTitle']
            player_name =  player['gameName'] + '#' + player['tagLine']
            player_level = player['accountLevel']
            player_kill = stats['kills']
            player_death = stats['deaths']
            player_assist = stats['assists']
            player_score = stats['score']
            player_rounds = stats['roundsPlayed']
            player_playtimeMillis = stats['playtimeMillis']

            if player_subject == puuid:
                your_name = player_name
                your_agent = agent_uuid
                your_team = player_team_id
                your_rank = player_competitiveTier
                your_KDA = f'{player_kill}/{player_death}/{player_assist}'
            
            player_stats_insert['team'] = player_team_id
            player_stats_insert['player'] = player_name
            player_stats_insert['agent_uuid'] = agent_uuid
            player_stats_insert['rank_tier'] = player_competitiveTier
            player_stats_insert['playercard_uuid'] = player_card
            player_stats_insert['title_uuid'] = player_title
            player_stats_insert['level'] = player_level
            player_stats_insert['stats']['kills'] = player_kill
            player_stats_insert['stats']['deaths'] = player_death
            player_stats_insert['stats']['assists'] = player_assist
            player_stats_insert['stats']['score'] = player_score
            player_stats_insert['stats']['rounds'] = player_rounds
            player_stats_insert['stats']['playtimeMillis'] = player_playtimeMillis
            if abilityCasts is not None:
                player_stats_insert['stats']['ability'] = {
                    'grenade': abilityCasts['grenadeCasts'],
                    'ability1': abilityCasts['ability1Casts'],
                    'ability2': abilityCasts['ability2Casts'],
                    'ultimate': abilityCasts['ultimateCasts'],
                }

        timelines = []

        is_surrendered = False
        for result in match_details['roundResults']:
            
            round_result_code = result['roundResultCode']
            if round_result_code == 'Surrendered' and is_surrendered is False:
                emoji = EmojiResult.get('Surrendered', '')
                is_surrendered = True
            elif result['winningTeam'] == your_team:
                emoji = EmojiResult.get(round_result_code + 'Win', '')
            else:
                emoji = EmojiResult.get(round_result_code + 'Loss', '')
                        
            timelines.append(emoji)
            if result['roundNum'] == 11 and is_surrendered is False:
                timelines.append(' | ')

            # bombPlanter
            round_planter = result.get('bombPlanter', None)
            if round_planter is not None:
                player_stats[round_planter]['stats']['plants'] += 1
            
            # bombDefuser
            round_defuse = result.get('bombDefuser', None)
            if round_defuse is not None:
                player_stats[round_defuse]['stats']['defuses'] += 1

            first_death = []
            for player in result['playerStats']:
                subject = player['subject']
                for dmg in player['damage']:
                    player_stats[subject]['stats']['damage']['total'] += dmg.get('damage', 0)
                    player_stats[subject]['stats']['damage']['headshots'] += dmg.get('headshots', 0)
                    player_stats[subject]['stats']['damage']['bodyshots'] += dmg.get('bodyshots', 0)
                    player_stats[subject]['stats']['damage']['legshots'] += dmg.get('legshots', 0)
                
                for kill in player['kills']:
                    first_death.append({
                        'killer': kill['killer'],
                        'victim': kill['victim'],
                        'roundTime': kill['roundTime'],
                    })

                if len(player['kills']) >= 3:
                    player_stats[subject]['stats']['multikills'] += 1
            
            if len(first_death) != 0:
                first_blood = sorted(first_death, key=lambda x: x['roundTime'])[0]
                first_kill = first_blood['killer']
                first_death = first_blood['victim']
                player_stats[first_kill]['stats']['firstkills'] += 1
                player_stats[first_death]['stats']['firstdeaths'] += 1

            # for player_eco in result['playerEconomies']:
            #     subject_eco = player_eco['subject']

            #     eco_stats = player_stats[subject_eco]
            #     eco_stats['stats']['loadoutValue'] += player_eco['loadoutValue']
            #     eco_stats['stats']['spent'] += player_eco['spent']

            #     player_team = eco_stats['team']
            #     if player_team == 'Blue':
            #         blue_loadout += player_eco['loadoutValue']
            #         blue_spent += player_eco['spent']
            #         blue_remaining += player_eco['remaining']
            #     elif player_team == 'Red':
            #         red_loadout += player_eco['loadoutValue']
            #         red_spent += player_eco['spent']
            #         red_remaining += player_eco['remaining']

        match_results = dict(
            MatchID=matchId,
            MapID=MapId,
            playdate=playdate,
            queueID=queueID,
            gamelength=gameLengthMillis,
            your_puuid=puuid,
            your_name=your_name,
            your_team=your_team,
            your_agent=your_agent,
            your_rank=your_rank,
            your_KDA=your_KDA,
            won=winner,
            loser=loser,
            winner_score=winner_score,
            loser_score=loser_score,
            rounds=winner_score + loser_score,
            blueteam=blueteam_uuid,
            redteam=redteam_uuid,
            player=player_stats,
            timelines=timelines
        )
        return match_results

# USEFUL

def iso_to_time(iso: datetime) -> datetime:
    '''Convert ISO time to datetime'''
    timestamp = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S%z").timestamp()
    time = datetime.utcfromtimestamp(timestamp)
    return time

def get_season_by_content(content: Dict) -> Tuple[str, str]:
    '''Get season id by content'''

    try:
        season_data = [season for season in content["Seasons"] if season["IsActive"] and season["Type"] == "act"]
        season_id = season_data[0]['ID']
        season_end = iso_to_time(season_data[0]['EndTime'])
        
    except (IndexError, KeyError, TypeError):
        season_id = 'd80f3ef5-44f5-8d70-6935-f2840b2d3882'
        season_end = datetime(2022, 6, 22, 17, 0, 0)
    
    return {'id': season_id, 'end': season_end}

# ---------- BATTLEPASS ---------- #

