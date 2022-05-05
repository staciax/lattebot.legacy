# Standard
import requests
import urllib3
import json
from typing import Union, Dict, List

# Local
from .resources import region_shard_override, shard_region_override
from .resources import base_endpoint
from .resources import base_endpoint_glz
from .resources import base_endpoint_shared
from .resources import queues 

# from .auth import Auth

# exceptions
from .errors import PhaseError, ResponseError
from .locale import LocaleErrorResponse

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class VALORANT_ENDPOINT:

    # __slots__ = (
    #     'puuid',
    #     'player_ign',
    #     'headers',
    #     'region',
    #     'pd',
    #     'shared',
    #     'glz',
    #     'active_season',
    #     'session',
    #     'shard',
    #     'client_platform'
    # )

    def __init__(self) -> None:
        
        # session
        self.session = requests.session()

        '''
        NOTE user_data format
        {
            'puuid': PUUID,
            'region': REGION,
            'headers': HEADERS,
        }
        '''

        # self.user_data = user_data

        self.headers = {}
        self.puuid = ''
        self.player = ''
        self.region = ''
        self.shard = ''

        self.pd = ''
        self.shared = ''
        self.glz = ''
        self.client_platform = 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9'
        
        # default region
        self.locale_code = 'en-US'

    def activate(self, auth: Dict) -> None:
        '''activate api'''

        try:
            headers = self.__build_headers(auth['headers'])
            self.headers = headers
            self.puuid = auth['puuid']
            self.region = auth['region']
            self.player = auth['player_name']
            self.locale_code = auth.get('locale_code', 'en-US')
            self.__format_region()
            self.__build_urls()
        except:
            raise ResponseError("Failed to activate API")

    def __verify_status_code(self, status_code, exceptions={}) -> None:
        '''Verify that the request was successful according to exceptions'''
        if status_code in exceptions.keys():
            response_exception = exceptions[status_code]
            raise response_exception[0](response_exception[1])

    def fetch(self, endpoint: str='/', url: str='pd', errors: Dict={}) -> Dict:
        endpoint_url = getattr(self, url)
        
        data = None
        r = self.session.get('{url}{endpoint}'.format(url=endpoint_url, endpoint=endpoint), headers=self.headers)   
        
        # custom exceptions for http status codes
        self.__verify_status_code(r.status_code, errors)
        
        try:
            data = json.loads(r.text)
        except: # as no data is set, an exception will be raised later in the method
            pass
        
        if "httpStatus" not in data:
            return data

        if data["httpStatus"] == 400:
            response = LocaleErrorResponse('AUTH', self.locale_code)
            raise RuntimeError(response.get('COOKIES_EXPIRED'))
            # self.activate()
            # return self.fetch(endpoint=endpoint, url=url)

    def post(self, endpoint: str ='/', url: str ='pd', body: Dict={}, errors: Dict={}) -> Dict:
        endpoint_url = getattr(self, url) 
        
        data = None
        r = self.session.post('{url}{endpoint}'.format(url=endpoint_url, endpoint=endpoint), headers=self.headers, json=body)   

        # custom exceptions for http status codes
        self.__verify_status_code(r.status_code, errors)

        try:
            data = json.loads(r.text)
        except:
            data = None 
        
        return data

    def put(self, endpoint: str="/", url: str='pd', body: Dict={}, errors: Dict={}) -> Dict:
        
        body = body if type(body) is list else json.dumps(body)

        endpoint_url = getattr(self, url)
        data = None

        r = self.session.put('{url}{endpoint}'.format(url=endpoint_url, endpoint=endpoint), headers=self.headers, json=body)   
        data = json.loads(r.text)

        # custom exceptions for http status codes
        self.__verify_status_code(r.status_code, errors)

        if data is not None:
            return data
        else:
            raise ResponseError("Request returned NoneType")

    def delete(self, endpoint: str='/', url: str='pd', body: Dict={}, errors: Dict={}) -> Dict:
        endpoint_url = getattr(self, url)
        data = None
        r = self.session.delete('{url}{endpoint}'.format(url=endpoint_url, endpoint=endpoint), headers=self.headers, data=json.dumps(body))   
        data = json.loads(r.text)

        # custom exceptions for http status codes
        self.__verify_status_code(r.status_code, errors)
        
        if data is not None:
            return data
        else:
            raise ResponseError("Request returned NoneType")

    # ------------------- #

    # contracts endpoints

    def fetch_contracts(self) -> Dict:
        '''
        Contracts_Fetch
        Get a list of contracts and completion status including match history       
        '''
        data = self.fetch(endpoint=f'/contracts/v1/contracts/{self.puuid}', url='pd')
        return data

    def contracts_activate(self, contract_id: str) -> Dict:
        '''
        Contracts_Activate
        Activate a particular contract      
        {contract id}: The ID of the contract to activate. Can be found from the ContractDefinitions_Fetch endpoint.
        '''
        data = self.post(endpoint=f'/contracts/v1/contracts/{self.puuid}/special/{contract_id}', url='pd')
        return data 

    def contracts_fetch_active_story(self) -> Dict:
        '''
        ContractDefinitions_FetchActiveStory
        Get the battlepass contracts      
        '''
        data = self.fetch(endpoint=f'/contract-definitions/v2/definitions/story', url='pd')
        return data 

    def itemprogress_fetch_definitions(self) -> Dict:
        '''
        ItemProgressDefinitionsV2_Fetch
        Fetch definitions for skin upgrade progressions
        '''
        data = self.fetch(endpoint=f'/contract-definitions/v3/item-upgrades', url='pd')
        return data

    def contracts_unlock_item_progress(self, progression_id: str) -> Dict:
        '''
        Contracts_UnlockItemProgressV2
        Unlock an item progression
        '''
        data = self.post(endpoint=f'/contracts/v2/item-upgrades/{progression_id}/{self.puuid}', url='pd')
        return data

    # PVP endpoints

    def fetch_content(self) -> Dict:
        '''
        Content_FetchContent
        Get names and ids for game content such as agents, maps, guns, etc.
        '''
        data = self.fetch(endpoint='/content-service/v3/content', url='shared')
        return data

    def fetch_account_xp(self) -> Dict:
        '''
        AccountXP_GetPlayer
        Get the account level, XP, and XP history for the active player
        '''
        data = self.fetch(endpoint=f'/account-xp/v1/players/{self.puuid}', url='pd')
        return data
    
    def fetch_player_loadout(self) -> Dict:
        '''
        playerLoadoutUpdate
        Get the player's current loadout
        '''
        data = self.fetch(endpoint=f'/personalization/v2/players/{self.puuid}/playerloadout', url='pd')
        return data

    def put_player_loadout(self, loadout: Dict) -> Dict:
        '''
        playerLoadoutUpdate
        Use the values from `fetch_player_loadout` excluding properties like `subject` and `version.` Loadout changes take effect when starting a new game
        '''
        data = self.put(endpoint=f'/personalization/v2/players/{self.puuid}/playerloadout', url='pd', body=loadout)
        return data

    def fetch_player_mmr(self, puuid:str=None) -> Dict:
        puuid = self.__check_puuid(puuid)
        data = self.fetch(endpoint=f'/mmr/v1/players/{puuid}', url='pd')
        return data

    def fetch_match_history(self, puuid: str=None, start_index: int=0, end_index: int=15, queue_id: str="null") -> Dict:
        '''
        MatchHistory_FetchMatchHistory
        Get recent matches for a player
        There are 3 optional query parameters: start_index, end_index, and queue_id. queue can be one of null, competitive, custom, deathmatch, ggteam, newmap, onefa, snowball, spikerush, or unrated.
        '''
        self.__check_queue_type(queue_id)
        puuid = self.__check_puuid(puuid)
        data = self.fetch(endpoint=f'/match-history/v1/history/{puuid}?startIndex={start_index}&endIndex={end_index}' + (f'&queue={queue_id}' if queue_id != 'null' else ''), url='pd')
        return data

    def fetch_match_details(self, match_id: str) -> Dict:
        '''
        Get the full info for a previous match
        Includes everything that the in-game match details screen shows including damage and kill positions, same as the official API w/ a production key
        '''
        data = self.fetch(endpoint=f'/match-details/v1/matches/{match_id}', url='pd')
        return data
    
    def fetch_competitive_updates(self, puuid: str=None, start_index: int=0, end_index: int=15, queue_id: str="competitive") -> Dict:
        '''
        MMR_FetchCompetitiveUpdates
        Get recent games and how they changed ranking
        There are 3 optional query parameters: start_index, end_index, and queue_id. queue can be one of null, competitive, custom, deathmatch, ggteam, newmap, onefa, snowball, spikerush, or unrated.
        '''
        self.__check_queue_type(queue_id)
        puuid = self.__check_puuid(puuid)
        data = self.fetch(endpoint=f'/mmr/v1/players/{puuid}/competitiveupdates?startIndex={start_index}&endIndex={end_index}' + (f'&queue={queue_id}' if queue_id != '' else ''), url='pd')
        return data

    def fetch_leaderboard(self, season: str, start_index: int=0, size: int=25) -> Dict:
        '''
        MMR_FetchLeaderboard
        Get the competitive leaderboard for a given season
        The query parameter query can be added to search for a username.
        '''
        if season == '': season = self.__get_live_season()
        data = self.fetch(f'/mmr/v1/leaderboards/affinity/{self.region}/queue/competitive/season/{season}?startIndex={start_index}&size={size}', url='pd')
        return data

    def fetch_player_restrictions(self) -> Dict:
        '''
        Restrictions_FetchPlayerRestrictionsV2
        Checks for any gameplay penalties on the account
        '''
        data = self.fetch(f'/restrictions/v2/penalties', url='pd')
        return data

    def fetch_item_progression_definitions(self) -> Dict:
        '''
        ItemProgressionDefinitionsV2_Fetch
        Get details for item upgrades
        '''
        data = self.fetch('/contract-definitions/v3/item-upgrades', url='pd')
        return data

    def fetch_config(self) -> Dict:
        '''
        Config_FetchConfig
        Get various internal game configuration settings set by Riot
        '''
        data = self.fetch(f'/v1/config/{self.region}', url='shared')
        return data

    def fetch_name_by_puuid(self, puuid:str=None) -> Dict:
        '''
        Name_service
        get player name tag by puuid
        NOTE:
        format ['PUUID']
        '''
        if puuid is None:
            puuid = [self.__check_puuid()]
        elif puuid is not None and type(puuid) is str:
            puuid = [puuid]
        data = self.put(endpoint='/name-service/v2/players', url='pd', body=puuid)
        return data

    # store endpoints
    def store_fetch_offers(self) -> Dict:
        '''
        Store_GetOffers
        Get prices for all store items
        '''
        data = self.fetch('/store/v1/offers/', url='pd')
        return data 

    def store_fetch_storefront(self) -> Dict:
        '''
        Store_GetStorefrontV2
        Get the currently available items in the store
        '''
        data = self.fetch(f'/store/v2/storefront/{self.puuid}', url='pd')
        return data 

    def store_fetch_wallet(self) -> Dict:
        '''
        Store_GetWallet
        Get amount of Valorant points and Radianite the player has
        Valorant points have the id 85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741 and Radianite points have the id e59aa87c-4cbf-517a-5983-6e81511be9b7        
        '''
        data = self.fetch(f'/store/v1/wallet/{self.puuid}', url='pd')
        # balances = {
        #     'vp': data["Balances"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"],
        #     'rad': data["Balances"]["e59aa87c-4cbf-517a-5983-6e81511be9b7"]
        # }
        return data 

    def store_fetch_order(self, order_id: str) -> Dict:
        '''
        Store_GetOrder
        {order id}: The ID of the order. Can be obtained when creating an order.
        '''
        data = self.fetch(f'/store/v1/order/{order_id}', url='pd')
        return data 

    def store_fetch_entitlements(self, item_type: Dict) -> Dict:
        '''
        Store_GetEntitlements
        List what the player owns (agents, skins, buddies, ect.)
        Correlate with the UUIDs in `fetch_content` to know what items are owned.
        Category names and IDs:
       
        `ITEMTYPEID:`
        '01bb38e1-da47-4e6a-9b3d-945fe4655707': 'Agents'\n
        'f85cb6f7-33e5-4dc8-b609-ec7212301948': 'Contracts',\n
        'd5f120f8-ff8c-4aac-92ea-f2b5acbe9475': 'Sprays',\n
        'dd3bf334-87f3-40bd-b043-682a57a8dc3a': 'Gun Buddies',\n
        '3f296c07-64c3-494c-923b-fe692a4fa1bd': 'Player Cards',\n
        'e7c63390-eda7-46e0-bb7a-a6abdacd2433': 'Skins',\n
        '3ad1b2b2-acdb-4524-852f-954a76ddae0a': 'Skins chroma',\n
        'de7caa6b-adf7-4588-bbd1-143831e786c6': 'Player titles',\n
        '''
        data = self.fetch(endpoint=f"/store/v1/entitlements/{self.puuid}/{item_type}", url="pd")
        return data

    # party endpoints
    
    def party_fetch_player(self) -> Dict:
        '''
        Party_FetchPlayer
        Get the Party ID that a given player belongs to                
        '''
        data = self.fetch(endpoint=f'/parties/v1/players/{self.puuid}', url='glz')
        return data

    def party_remove_player(self, puuid: str) -> Dict:
        '''
        Party_RemovePlayer
        Removes a player from the current party      
        '''
        puuid = self.__check_puuid(puuid)
        data = self.delete(endpoint=f'/parties/v1/players/{puuid}', url='glz')
        return data
    
    def fetch_party(self) -> Dict:
        '''
        Party_FetchParty
        Get details about a given party id    
        '''
        party_id = self.__get_current_party_id()
        data = self.fetch(endpoint=f'/parties/v1/parties/{party_id}', url='glz')
        return data

    def party_set_member_ready(self, party_id, ready:bool=True) -> Dict:
        '''
        Party_SetMemberReady
        Sets whether a party member is ready for queueing or not      
        '''
        data = self.post(endpoint='/parties/v1/parties/{party}/members/{puuid}/setReady'.format(party=party_id, puuid=self.puuid), url='glz', body={"ready": ready})
        return data

    def party_refresh_competitive_tier(self) -> Dict:
        '''
        Party_RefreshCompetitiveTier
        Refreshes the competitive tier for a player    
        '''
        party_id = self.__get_current_party_id()
        data = self.post(endpoint=f'/parties/v1/parties/{party_id}/members/{self.puuid}/refreshCompetitiveTier', url='glz')
        return data

    def party_refresh_player_identity(self) -> Dict:
        '''
        Party_RefreshPlayerIdentity
        Refreshes the identity for a player   
        '''
        party_id = self.__get_current_party_id()
        data = self.post(endpoint=f'/parties/v1/parties/{party_id}/members/{self.puuid}/refreshPlayerIdentity', url='glz')
        return data

    def party_refresh_pings(self) -> Dict:
        '''
        Party_RefreshPings
        Refreshes the pings for a player      
        '''
        party_id = self.__get_current_party_id()
        data = self.post(endpoint=f'/parties/v1/parties/{party_id}/members/{self.puuid}/refreshPings', url='glz')
        return data

    def party_change_queue(self, queue_id: str) -> Dict:
        '''
        Party_ChangeQueue
        Sets the matchmaking queue for the party 
        '''
        self.__check_queue_type(queue_id)
        party_id = self.__get_current_party_id()
        data = self.post(endpoint=f'/parties/v1/parties/{party_id}/queue', url='glz', body={"queueID": queue_id})
        return data

    def party_start_custom_game(self) -> Dict:
        '''
        Party_StartCustomGame
        Starts a custom game     
        '''
        party_id = self.__get_current_party_id()
        data = self.post(endpoint=f'/parties/v1/parties/{party_id}/startcustomgame', url='glz')
        return data

    def party_enter_matchmaking_queue(self) -> Dict:
        '''
        Party_EnterMatchmakingQueue
        Enters the matchmaking queue
        '''
        party_id = self.__get_current_party_id()
        data = self.post(endpoint=f'/parties/v1/parties/{party_id}/matchmaking/join', url='glz')
        return data

    def party_leave_matchmaking_queue(self) -> Dict:
        '''
        Party_LeaveMatchmakingQueue
        Leaves the matchmaking queue   
        '''
        party_id = self.__get_current_party_id()
        data = self.post(endpoint=f'/parties/v1/parties/{party_id}/matchmaking/leave', url='glz')
        return data

    def set_party_accessibility(self, open:bool) -> Dict:
        '''
        Party_SetAccessibility
        Changes the party accessibility to be open or closed  
        '''
        state = "OPEN" if open else "CLOSED"
        party_id = self.__get_current_party_id()
        data = self.post(endpoint=f'/parties/v1/parties/{party_id}/accessibility', url='glz', body={"accessibility": state})
        return data

    def party_set_custom_game_settings(self, party_id, settings: Dict) -> Dict:
        '''
        Party_SetCustomGameSettings
        Changes the settings for a custom game

        settings:
        {
            "Map": "/Game/Maps/Triad/Triad", # map url
            "Mode": "/Game/GameModes/Bomb/BombGameMode.BombGameMode_C", # url to gamemode
            "UseBots": true, # this isn't used anymore :(
            "GamePod": "aresriot.aws-rclusterprod-use1-1.na-gp-ashburn-awsedge-1", # server
            GameRules": {
                "AllowGameModifiers": "true/false",
                "PlayOutAllRounds": "true/false",
                "SkipMatchHistory": "true/false",
                "TournamentMode": "true/false",
                "IsOvertimeWinByTwo": "true/false",
            }
        }
        '''
        party_id = self.__get_current_party_id()
        data  = self.post(endpoint=f'/parties/v1/parties/{party_id}/customgamesettings', url='glz', body=settings)
        return data

    def party_invite_by_display_name(self, name: str, tag: str) -> Dict:
        '''
        Party_InviteToPartyByDisplayName
        Invites a player to the party with their display name
        like name=asuna, tag=1234 >>> asuna#1234
        '''
        party_id = self.__get_current_party_id()
        data = self.post(endpoint=f'/parties/v1/parties/{party_id}/invites/name/{name}/tag/{tag}')
        return data

    def party_request_to_join(self, party_id: str, other_puuid: str) -> Dict:
        '''
        Party_RequestToJoinParty
        Requests to join a party
        '''
        data = self.post(endpoint=f'/parties/v1/parties/{party_id}/request', body={"Subjects":[other_puuid]})
        return data
    
    def party_decline_request(self, request_id: str) -> Dict:
        '''
        Party_DeclineRequest
        Declines a party request
        {request id}: The ID of the party request. Can be found from the Requests array on the Party_FetchParty endpoint.
        '''
        party_id = self.__get_current_party_id()
        data = self.post(endpoint=f'/parties/v1/parties/{party_id}/request/{request_id}/decline', url='glz')
        return data

    def party_join(self, party_id: str) -> Dict:
        '''
        Party_PlayerJoin
        Join a party
        '''
        data = self.post(endpoint=f'/parties/v1/players/{self.puuid}/joinparty/{party_id}', url='glz')
        return data 

    def party_leave(self, party_id: str) -> Dict:
        '''
        Party_PlayerLeave
        Leave a party
        '''
        data = self.post(endpoint=f'/parties/v1/players/{self.puuid}/leaveparty/{party_id}', url='glz')
        return data

    def party_fetch_custom_game_configs(self) -> Dict:
        '''
        Party_FetchCustomGameConfigs
        Get information about the available gamemodes
        '''
        data = self.fetch(endpoint='/parties/v1/parties/customgameconfigs', url='glz')
        return data

    def party_fetch_muc_token(self) -> Dict:
        '''
        Party_FetchMUCToken
        Get a token for party chat
        '''
        party_id = self.__get_current_party_id()
        data = self.fetch(endpoint=f'/parties/v1/parties/{party_id}/muctoken', url='glz')
        return data

    def party_fetch_voice_token(self) -> Dict:
        '''
        Party_FetchVoiceToken
        Get a token for party voice
        '''
        party_id = self.__get_current_party_id()
        data = self.fetch(endpoint=f'/parties/v1/parties/{party_id}/voicetoken', url="glz")
        return data
    
    # PRE-GAME

    def pregame_fetch_player(self) -> Dict:
        '''
        Pregame_GetPlayer
        Get the ID of a game in the pre-game stage       
        '''
        data = self.fetch(endpoint=f'/pregame/v1/players/{self.puuid}', url='glz', errors={404: [PhaseError, 'You are not in a pre-game']})
        return data
    
    def pregame_fetch_match(self, match_id:str=None) -> Dict:
        '''
        Pregame_GetMatch
        Get info for a game in the pre-game stage       
        '''
        match_id = self.__pregame_check_match_id(match_id)
        data = self.fetch(endpoint=f'/pregame/v1/matches/{match_id}', url='glz', errors={404: [PhaseError, 'You are not in a pre-game']})
        return data

    def pregame_fetch_match_loadouts(self, match_id:str=None) -> dict:
        '''
        Pregame_GetMatchLoadouts
        Get player skins and sprays for a game in the pre-game stage      
        '''
        match_id = self.__pregame_check_match_id(match_id)
        data = self.fetch(f'/pregame/v1/matches/{match_id}/loadouts', url='glz', errors={404: [PhaseError, 'You are not in a pre-game']})
        return data
    
    def pregame_fetch_chat_token(self, match_id: str=None) -> Dict:
        '''
        Pregame_FetchChatToken
        Get a chat token     
        '''
        match_id = self.__pregame_check_match_id(match_id)
        data = self.fetch(endpoint=f'/pregame/v1/matches/{match_id}/chattoken', url='glz', errors={404: [PhaseError, 'You are not in a pre-game']})
        return data 

    def pregame_fetch_voice_token(self, match_id: str=None) -> Dict:
        '''
        Pregame_FetchVoiceToken
        Get a voice token      
        '''
        match_id = self.__pregame_check_match_id(match_id)
        data = self.fetch(endpoint=f'/pregame/v1/matches/{match_id}/voicetoken', url='glz', errors={404: [PhaseError, 'You are not in a pre-game']})
        return data 

    def pregame_select_character(self, agent_id: str, match_id: str=None):
        '''
        Pregame_SelectCharacter
        Select an agent
        don't use this for instalocking :)
        '''
        match_id = self.__pregame_check_match_id(match_id)
        data = self.post(endpoint=f'/pregame/v1/matches/{match_id}/select/{agent_id}', url='glz', errors={404: [PhaseError, 'You are not in a pre-game']})
        return data
    
    def pregame_lock_character(self, agent_id: str, match_id: str=None) -> Dict:
        '''
        Pregame_LockCharacter
        Lock in an agent
        don't use this for instalocking :)       
        '''
        match_id = self.__pregame_check_match_id(match_id)
        data = self.post(endpoint=f'/pregame/v1/matches/{match_id}/lock/{agent_id}', url='glz', errors={404: [PhaseError, 'You are not in a pre-game']})
        return data

    def pregame_quit_match(self, match_id: str=None) -> Dict:
        '''
        Pregame_QuitMatch
        Quit a match in the pre-game stage     
        '''
        match_id = self.__pregame_check_match_id(match_id)
        data = self.post(endpoint=f'/pregame/v1/matches/{match_id}/quit', url='glz', errors={404: [PhaseError, 'You are not in a pre-game']})
        return data

    # CURRENT-GAME
    def coregame_fetch_player(self) -> Dict:
        '''
        CoreGame_FetchPlayer
        Get the game ID for an ongoing game the player is in        
        '''
        data = self.fetch(endpoint=f'/core-game/v1/players/{self.puuid}', url='glz', errors={404: [PhaseError, "You are not in a core-game"]})
        return data

    def coregame_fetch_match(self, match_id: str=None) -> Dict:
        '''
        CoreGame_FetchMatch
        Get information about an ongoing game      
        '''
        match_id = self.__coregame_check_match_id(match_id)
        data = self.fetch(endpoint=f'/core-game/v1/matches/{match_id}', url='glz', errors={404: [PhaseError, "You are not in a core-game"]})
        return data
    
    def coregame_fetch_match_loadouts(self, match_id:str=None) -> Dict:
        '''
        CoreGame_FetchMatchLoadouts
        Get player skins and sprays for an ongoing game     
        '''
        match_id = self.__coregame_check_match_id(match_id)
        data = self.fetch(endpoint=f'/core-game/v1/matches/{match_id}/loadouts', url='glz', errors={404: [PhaseError, "You are not in a core-game"]})
        return data

    def coregame_fetch_team_chat_muc_token(self, match_id: str=None) -> Dict:
        '''
        CoreGame_FetchTeamChatMUCToken
        Get a token for team chat    
        '''
        match_id = self.__coregame_check_match_id(match_id)
        data = self.fetch(endpoint=f'/core-game/v1/matches/{match_id}/teamchatmuctoken', url="glz", errors={404: [PhaseError, "You are not in a core-game"]})
        return data

    def coregame_fetch_allchat_muc_token(self, match_id: str=None) -> Dict:
        '''
        CoreGame_FetchAllChatMUCToken
        Get a token for all chat      
        '''
        match_id = self.__coregame_check_match_id(match_id)
        data = self.fetch(endpoint=f'/core-game/v1/matches/{match_id}/allchatmuctoken', url='glz', errors={404: [PhaseError, "You are not in a core-game"]})
        return data

    def coregame_disassociate_player(self,match_id: str=None) -> Dict:
        '''
        CoreGame_DisassociatePlayer
        Leave an in-progress game    
        '''
        match_id = self.__coregame_check_match_id(match_id)
        data = self.post(endpoint=f'/core-game/v1/players/{self.puuid}/disassociate/{match_id}', url='glz', errors={404: [PhaseError, "You are not in a core-game"]})
        return data


    # session endpoints
   
    def session_fetch(self) -> Dict:
        '''
        Session_Get
        Get information about the current game session     
        '''
        data = self.fetch(endpoint=f'/session/v1/sessions/{self.puuid}', url='glz')
        return data 

    def session_reconnect(self) -> Dict:
        '''
        Session_ReConnect
        '''
        data = self.fetch(endpoint=f'/session/v1/sessions/{self.puuid}/reconnect', url='glz')
        return data 

    # useful endpoints

    def fetch_mission(self):
        '''
        Get player daily/weekly missions
        '''
        data = self.fetch_contracts()
        mission = data["Missions"]
        return mission

    def get_player_level(self):
        '''
        Aliases `fetch_account_xp` but received a level
        '''
        data = self.fetch_account_xp()['Progress']['Level']
        return data
    
    def get_player_tier_rank(self, puuid: str=None) -> str:
        '''
        get player current tier rank
        '''
        data = self.fetch_player_mmr(puuid)
        season_id = data['LatestCompetitiveUpdate']['SeasonID']
        if len(season_id) == 0:
            season_id = self.__get_live_season()
        current_season = data["QueueSkills"]['competitive']['SeasonalInfoBySeasonID']
        current_Tier = current_season[season_id]['CompetitiveTier']
        return current_Tier

    # local utility functions
    
    def __get_live_season(self) -> str:
        '''Get the UUID of the live competitive season'''
        content = self.fetch_content()
        season_id = [season["ID"] for season in content["Seasons"] if season["IsActive"] and season["Type"] == "act"]
        if not season_id:
            return self.fetch_player_mmr()["LatestCompetitiveUpdate"]["SeasonID"]
        return season_id[0]

    def __check_puuid(self, puuid: str) -> str:
        '''If puuid passed into method is None make it current user's puuid'''
        return self.puuid if puuid is None else puuid

    def __check_party_id(self, party_id: str) -> str:
        '''If party ID passed into method is None make it user's current party'''
        return self.__get_current_party_id() if party_id is None else party_id

    def __get_current_party_id(self) -> str:
        '''Get the user's current party ID'''
        party = self.party_fetch_player()
        return party["CurrentPartyID"]

    def __coregame_check_match_id(self, match_id: str) -> str:
        '''Check if a match id was passed into the method'''
        return self.coregame_fetch_player()["MatchID"] if match_id is None else match_id

    def __pregame_check_match_id(self, match_id: str) -> str:
        return self.pregame_fetch_player()["MatchID"] if match_id is None else match_id

    def __check_queue_type(self, queue_id: str) -> None:
        '''Check if queue id is valid'''
        if queue_id not in queues:
            raise ValueError("Invalid queue type")
    
    def __build_urls(self) -> str:
        '''
        generate URLs based on region/shard
        '''
        self.pd = base_endpoint.format(shard=self.shard)
        self.shared = base_endpoint_shared.format(shard=self.shard)
        self.glz = base_endpoint_glz.format(region=self.region, shard=self.shard)

    def __build_headers(self, headers: Dict) -> Dict:

        try:
            headers = json.loads(headers)
        except TypeError:
            headers = headers
        headers['X-Riot-ClientPlatform'] = self.client_platform
        headers['X-Riot-ClientVersion'] = self.__get_current_version()
        return headers
            
    # def __get_headers(self) -> Dict:
    #     '''Get authorization headers to make requests'''
    #     try: 
    #         puuid, headers, region, ign = self.auth.authenticate()
    #         headers['X-Riot-ClientPlatform'] = self.client_platform
    #         headers['X-Riot-ClientVersion'] = self.__get_current_version()
    #         return puuid, headers, region, ign
    #     except Exception as e:
    #         print(e)
    #         raise ResponseError('Authorization failed. plese try again')

    def __format_region(self) -> None:
        self.shard = self.region
        if self.region in region_shard_override.keys():
            self.shard = region_shard_override[self.region]
        if self.shard in shard_region_override.keys():
            self.region = shard_region_override[self.shard]

    def __get_current_version(self) -> str:
        data = self.session.get('https://valorant-api.com/v1/version')
        data = data.json()['data']
        return f"{data['branch']}-shipping-{data['buildVersion']}-{data['version'].split('.')[3]}" # return formatted version string