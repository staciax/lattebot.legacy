# Standard
import json
import re
import urllib3
from typing import Tuple, Dict, Optional

# Third
import requests
from .locale import LocaleErrorResponse

# Local

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_tokens_from_uri(URL: str, locale_code: str) -> Optional[Tuple[str, str]]:
    # language
    response = LocaleErrorResponse('AUTH', locale_code)
    
    try:
        accessToken = URL.split("access_token=")[1].split("&scope")[0]
        tokenId = URL.split("id_token=")[1].split("&")[0]
        return accessToken, tokenId
    except IndexError:
        raise RuntimeError(response.get('COOKIES_EXPIRED'))

def extract_tokens(data: str) -> str:
    """Extract tokens from data"""

    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    response = pattern.findall(data['response']['parameters']['uri'])[0]
    return response


class Auth:
    def __init__(self) -> None:
        self.user_agent = 'RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)'

        self.locale_code = 'en-US' # default language
        self.response = {} # prepare response for local response

    def local_response(self) -> LocaleErrorResponse:
        '''This function is used to check if the local response is enabled.'''
        self.response = LocaleErrorResponse('AUTH', self.locale_code)
        return self.response

    def authenticate(self, username:str, password: str) -> Dict:

        # language
        local_response = self.local_response()
        session = requests.session()

        # prepare cookies for auth request    
        
        data = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
            'scope': 'account openid',
        }
        
        headers = {'Content-Type': 'application/json', 'User-Agent': self.user_agent}

        r = session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
        
        cookies = {}
        cookies['cookie'] = r.cookies.get_dict()

        # get access token
        data = {"type": "auth", "username": username, "password": password, "remember": True}
        r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)

        session.close()
    
        for cookie in r.cookies.items():
            cookies['cookie'][cookie[0]] = cookie[1]
                
        if r.json()['type'] == 'response':
            
            data = extract_tokens(r.json())
            access_token = data[0]
            token_id = data[1]

            return {'auth': 'response', 'data': {'cookie': cookies, 'access_token': access_token, 'token_id': token_id}}
            
        elif r.json()['type'] == 'multifactor':
            if r.status_code == 429:
                raise RuntimeError(local_response.get('RATELIMIT'))

            label_modal = local_response.get('INPUT_2FA_CODE')
            WaitFor2FA = {"auth": "2fa", "cookie": cookies, 'label': label_modal}

            if r.json()['multifactor']['method'] == 'email':
                WaitFor2FA['message'] = f"{local_response.get('2FA_TO_EMAIL')} {r.json()['multifactor']['email']}"
                return WaitFor2FA
            
            WaitFor2FA['message'] = local_response.get('2FA_ENABLE')
            return WaitFor2FA
        
        raise RuntimeError(local_response.get('INVALID_PASSWORD'))

    def get_entitlements_token(self, access_token: str) -> Optional[str]:

        # language
        local_response = self.local_response()
        
        session = requests.session()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
        
        session.close()
        try:
            entitlements_token = r.json()['entitlements_token']
        except KeyError:
            raise RuntimeError(local_response.get('COOKIES_EXPIRED'))
        else:
            return entitlements_token

    def get_userinfo(self, access_token: str) -> Optional[str]:

        # language
        local_response = self.local_response()
        session = requests.session()
                
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        r = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})
        
        session.close()
        try:
            puuid = r.json()['sub']
            name = r.json()['acct']['game_name']
            tag = r.json()['acct']['tag_line']
        except KeyError:
            raise RuntimeError(local_response.get('NO_NAME_TAG'))
        else:
            return puuid, name, tag

    def get_region(self, access_token: str, token_id: str) -> Optional[str]:
        
        # language
        local_response = self.local_response()

        session = requests.session()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        body = {"id_token": token_id}
        r = session.put('https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', headers=headers, json=body)
        
        session.close()
        
        try:
            region = r.json()['affinities']['live']

        except KeyError:
            raise RuntimeError(local_response.get('REGION_NOT_FOUND'))
        else:
            return region 

    def give2facode(self, twoFAcode: str, cookies: Dict) -> Dict:
        session = requests.session()
        
        # language
        local_response = self.local_response()

        # LOAD COOKIE
        # cookies = json.loads(cookies)
        
        headers = {'Content-Type': 'application/json', 'User-Agent': self.user_agent}

        data = {"type": "multifactor", "code": twoFAcode, "rememberDevice": True}

        r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers, cookies=cookies['cookie'])
        
        session.close()

        if r.json()['type'] == 'response':
            cookies = {}
            cookies['cookie'] = r.cookies.get_dict()

            data = extract_tokens(r.json())
            access_token = data[0]
            token_id = data[1]
            
            return {'auth': 'response', 'data': {'cookie': cookies, 'access_token': access_token, 'token_id': token_id}}
        
        return {'auth': 'failed', 'error': local_response.get('2FA_INVALID_CODE')}

    def redeem_cookies(self, cookies: Dict, locale_code: str = 'en-US') -> Tuple[Dict, str, str]:

        # language
        local_response = self.local_response()
        
        # # LOAD COOKIE
        cookies = json.loads(cookies)

        old_cookie = cookies['cookie']

        session = requests.session()
        r = session.get(
            "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play-valorant-web-prod&response_type=token%20id_token&scope=account%20openid&nonce=1",
            cookies=cookies['cookie'],
            allow_redirects=False
        )

        if r.status_code != 303:
            raise RuntimeError(local_response.get('COOKIES_EXPIRED'))

        session.close()

        # NEW COOKIE
        cookies = {}
        cookies['cookie'] = old_cookie
        for cookie in r.cookies.items():
            cookies['cookie'][cookie[0]] = cookie[1]

        accessToken, tokenId = extract_tokens_from_uri(r.text, locale_code)
        entitlements_token = self.get_entitlements_token(accessToken)
        
        return cookies, accessToken, entitlements_token, tokenId

    def login_with_cookie(self, cookies: Dict, locale_code: str) -> Dict:
        
        session = requests.session()
        headers = {
            'cookie': cookies
        }
        r = session.get(
            "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id=play-valorant-web-prod&response_type=token%20id_token&scope=account%20openid&nonce=1",
            headers=headers,
            allow_redirects=False
        )

        session.close()
        
        # NEW COOKIE
        cookies = {}
        cookies['cookie'] = r.cookies.get_dict()
        accessToken, tokenID = extract_tokens_from_uri(r.text, locale_code)
        entitlements_token = self.get_entitlements_token(accessToken)

        data = {
            'cookies': cookies,
            'AccessToken': accessToken,
            'token_id': tokenID,
            'emt': entitlements_token
        }

        return data
    
    def temp_auth(self, username: str, password: str) -> Optional[Dict]:
        
        authenticate = self.authenticate(username, password)
        if authenticate['auth'] == 'response':
            access_token = authenticate['data']['access_token']
            token_id = authenticate['data']['token_id']

            entitlements_token = self.get_entitlements_token(access_token)
            puuid, name, tag = self.get_userinfo(access_token)
            region = self.get_region(access_token, token_id)
            player_name = f'{name}#{tag}' if tag is not None and tag is not None else 'no_username'

            headers = {'Authorization': f'Bearer {access_token}', 'X-Riot-Entitlements-JWT': entitlements_token}
            user_data = {'puuid': puuid, 'region': region, 'headers': headers, 'player_name': player_name}
            return user_data

        elif authenticate['auth'] == '2fa':
            return {'error': authenticate['message']}

        not_support = {
            "en-US": "Not supported 2FA, Please use `/login` and use other cmd without username, password.",
            "th": "เข้าสู่ระบบชั่วคราว ยังไม่รองรับ 2FA โปรดใช้ `/login` และใช้คำสั่งอื่นๆ โดยไม่มี username, password."
            } 
        
        raise RuntimeError(not_support.get(self.locale_code, not_support['en-US']))