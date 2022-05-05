import json
import os
import contextlib
from typing import Tuple, Dict, List
from datetime import datetime

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
        file_path = f"ext/valorant/data/"+ filename +".json"
        file_dir = os.path.dirname(file_path)
        os.makedirs(file_dir, exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w") as fp:
                json.dump(formats, fp, indent=2)

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

class GetFormat:

    def offer_format(data: Dict, language: str) -> Dict:
        '''Get skins format'''

        offer_list = data["SkinsPanelLayout"]["SingleItemOffers"]
        duration = data["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]

        skin_count = 0
        skin_source = {}
        
        for uuid in offer_list:
            skin = GetItem.get_skin(uuid)
            price = GetItem.get_skin_price(uuid)
            tier_icon = GetItem.get_skin_tier_icon(uuid)
            name, icon = skin['names'][language], skin['icon']

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

    def nightmarket_format(offer: Dict, language: str, response: Dict) -> Dict:
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
            
            uuid = offer['Offer']['ID']
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

    def mission_format(data: Dict, language:str) -> Dict[str, str]:
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
        
    def leaderboard_format(data: Dict) -> List[str]:
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
    def battlepass_format(cls, data: Dict, season: str, language: str) -> Dict:
        
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

        def get_contracts_uuid():
            try:
                data_contracts = JSON.read('contracts')
                contracts_uuid = [x for x in data_contracts['contracts'] if data_contracts['contracts'][x]['reward']['relationUuid'] == season_id]
            except KeyError:
                from .cache import fetch_contracts
                fetch_contracts()
                return get_contracts_uuid()
            
            return contracts_uuid
            
        contracts_uuid = get_contracts_uuid()
                
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

