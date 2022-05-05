import asyncpg
import json
import os
from dotenv import load_dotenv
load_dotenv()

from discord import Interaction
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from utils.formats import timestamp_utc
# from utils.auth import Auth
from .auth import Auth
from .locale import LocaleErrorResponse

from cryptography.fernet import Fernet

class ValorantDB:
    _version = 1

    def __init__(self, db: asyncpg.Pool, key: str) -> None:
        self.db  = db
        self.key = key
        self.auth = Auth()

    def encrypt(self, message: str, key: bytes) -> str:
        return str(Fernet(key).encrypt(message.encode())).split("'")[1]

    def decrypt(self, token: str, key: bytes) -> bytes:
        return Fernet(key).decrypt(bytes(token, "utf-8")).decode()

    async def is_login(self, user_id: int, login: bool=False) -> Optional[Dict]:
        
        db = self.db

        query = 'SELECT * FROM valorant.users WHERE user_id = $1;'
        row = await db.fetchrow(query, user_id)
    
        if row:
            return row
        elif login:
            return False
        else:
            raise RuntimeError("you're not registered!, plz `/login` to register!")

    async def login(self, user_id: int, data: dict, guild_id:int, locale_code: str, update:bool=False) -> Optional[Dict]:

        # language
        response = LocaleErrorResponse('DATABASE', locale_code)

        db = self.db
        auth = self.auth

        auth_data = data['data']
        cookies = json.dumps(auth_data['cookie'])
        access_token = auth_data['access_token']
        token_id = auth_data['token_id']

        entitlements_token = auth.get_entitlements_token(access_token)
        puuid, name, tag = auth.get_userinfo(access_token)
        region = auth.get_region(access_token, token_id)
        player_name = f'{name}#{tag}' if tag is not None and tag is not None else 'no_username'
        
        expiry_token = datetime.timestamp(datetime.utcnow() + timedelta(minutes=59))
        
        headers = json.dumps({'Authorization': f'Bearer {access_token}', 'X-Riot-Entitlements-JWT': entitlements_token})

        # encrypt data
        e_headers = self.encrypt(headers, self.key)
        e_cookies = self.encrypt(cookies, self.key)

        query = """INSERT INTO valorant.users(
                user_id, guild_id, puuid, player_name, region, expiry_token, headers, cookies, notify_mode)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);
                """

        if update:
            query = """UPDATE valorant.users
            SET guild_id=$2, puuid=$3, player_name=$4, region=$5, expiry_token=$6, headers=$7, cookies=$8, notify_mode=$9
            WHERE user_id = $1;
            """

        async with db.acquire():
            try:
                await db.execute(query, user_id, guild_id, puuid, player_name, region, int(expiry_token), e_headers, e_cookies, None)
            except asyncpg.UniqueViolationError as e:
                return {'auth': False, 'error': response.get('LOGIN_ERROR')}
            except Exception as e:
                print('error to login', e)
                return {'auth': False, 'error': response.get('LOGIN_ERROR')}
            else:
                return {'auth': True, 'player': player_name}

    async def remove_data(self, interaction: Interaction) -> Optional[Dict]:
        
        db = self.db
        user_id = interaction.user.id

        row = await self.is_login(user_id)
        
        if row:
            query = 'DELETE FROM valorant.users WHERE user_id = $1;'
            try:
                await db.execute(query, user_id)
            except:
                raise RuntimeError('error to remove data')
        
    async def refresh_token(self, user_id: int, cookies: Dict, locale_code: str) -> Optional[Dict]:
        
        auth = self.auth
        db = self.db

        new_cookie, access_token, entitlements_token, tokenId = auth.redeem_cookies(cookies, locale_code)

        EXP_TOKEN = datetime.timestamp(datetime.utcnow() + timedelta(minutes=59))

        new_header = {'Authorization': f'Bearer {access_token}', 'X-Riot-Entitlements-JWT': entitlements_token}

        cookie = json.dumps(new_cookie)
        header = json.dumps(new_header)

        e_cookies = self.encrypt(cookie, self.key)
        e_headers = self.encrypt(header, self.key)

        query = "UPDATE valorant.users SET expiry_token=$2, headers=$3, cookies=$4 WHERE user_id = $1;"
        await db.execute(query, user_id, EXP_TOKEN, e_headers, e_cookies)

        return header

    async def is_data(self, user_id:int, locale_code: str) -> Optional[Dict]:

        row = await self.is_login(user_id)  
    
        puuid = row['puuid']
        region = row['region']
        player_name = row['player_name']
        notify_mode = row['notify_mode']

        # decrypt data
        try:
            headers = self.decrypt(row['headers'], self.key)
            cookies = self.decrypt(row['cookies'], self.key)
        except: 
            headers = row['headers']
            cookies = row['cookies']

        if timestamp_utc() > row['expiry_token']:
            headers = await self.refresh_token(user_id, cookies, locale_code)

        data = dict(
            puuid=puuid,
            region=region,
            headers=headers,
            player_name=player_name,
            notify_mode=notify_mode
        )
           
        return data or None
    
    async def logout(self, user_id: int, locale_code: str) -> None:
        '''Logout from database'''

        response = LocaleErrorResponse('DATABASE', locale_code)

        query = f'DELETE FROM valorant.users WHERE user_id = $1 RETURNING user_id;'
        deleted = await self.db.fetchrow(query, user_id)

        if deleted is None:
            raise RuntimeError(response.get('LOGOUT_ERROR'))

        query = 'DELETE FROM valorant.users WHERE user_id = $1;'
        await self.db.execute(query, user_id)

    async def cookie_login(self, user_id: int, input_cookie: str, guild_id:str, locale_code: str) -> Optional[Dict]:
        db = self.db

        auth = self.auth
        data = auth.login_with_cookie(input_cookie, locale_code)

        cookie = data['cookies']
        access_token = data['AccessToken']
        token_id = data['token_id']
        entitlements_token = data['emt']
        
        puuid, name, tag = auth.get_userinfo(access_token)
        region = auth.get_region(access_token, token_id)
        player_name = f'{name}#{tag}' if tag is not None and tag is not None else 'no_username'

        expiry_token = datetime.timestamp(datetime.utcnow() + timedelta(minutes=59))

        headers = {'Authorization': f'Bearer {access_token}', 'X-Riot-Entitlements-JWT': entitlements_token}
        COOKIE = json.dumps(cookie)
        HEADER = json.dumps(headers)
        
        query = """INSERT INTO valorant.users(
                user_id, guild_id, puuid, player_name, region, expiry_token, headers, cookies, notify_mode)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);
                """
                            
        async with db.acquire():
            try:
                await db.execute(query, user_id, guild_id, puuid, player_name, region, int(expiry_token), HEADER, COOKIE, None)
            except asyncpg.UniqueViolationError as e:
                return {'auth': False, 'error': e}
            except Exception as e:
                return {'auth': False, 'error': e}
            else:
                return {'auth': True, 'player': player_name}

    async def delete_guild(self, guild_id: int) -> None:
        '''clear all userdata from specific guild'''

        # remove all userdata from guild
        query = 'DELETE FROM valorant.users WHERE guild_id = $1;'
        await self.db.execute(query, guild_id)
        
        # remove all notification from guild
        query = 'DELETE FROM valorant.notifys WHERE guild_id = $1;'
        await self.db.execute(query, guild_id)

    # async def delete_user(self, user_id: int) -> None:
    #     # remove all userdata from user_id
    #     query = 'DELETE FROM valorant.users WHERE user_id = $1;'
    #     await self.db.execute(query, user_id)
        
    #     # remove all notification from user_id
    #     query = 'DELETE FROM valorant.notifys WHERE user_id = $1;'
    #     await self.db.execute(query, user_id)

    async def delete_user_notify(self, user_id: int) -> None:        
        # remove all notification from guild
        query = 'DELETE FROM valorant.notifys WHERE user_id = $1;'
        await self.db.execute(query, user_id)

    async def _get_all_notify_users(self) -> Optional[Dict]:
        query = 'SELECT * FROM valorant.users WHERE notify_mode IS NOT NULL;'
        data = await self.db.fetch(query)
        return data
    
    async def _get_notify_mode(self, user_id: int) -> str:
        query = 'SELECT notify_mode FROM valorant.users WHERE user_id = $1;'
        data = await self.db.fetchrow(query, user_id)
        return data['notify_mode']
    
    # async def _get_all_users(self) -> Optional[dict]:
    #     '''Get all data in database'''
    #     query = 'SELECT * FROM valorant.users;'
    #     data = await self.db.fetch(query)
    #     return data
    
    async def _get_all_notifys(self) -> Optional[Dict]:
        '''Get all data in notifys'''
        query = 'SELECT * FROM valorant.notifys;'
        data = await self.db.fetch(query)
        return data
    
    async def _get_notify_ByUserID(self, user_id: int) -> Optional[Dict]:
        query = 'SELECT * FROM valorant.notifys WHERE user_id = $1;'
        row = await self.db.fetch(query, user_id)
        return row
    
    # async def _notify_count(self, user_id: int) -> None:
    #     query = 'SELECT COUNT(*) FROM valorant.notifys WHERE user_id = $1;'
    #     count = await self.db.fetchval(query, user_id)
    #     return count

    async def get_notify_user(self, user_id: int) -> Optional[Dict]:
        select = 'SELECT * FROM valorant.notifys WHERE user_id = $1'
        row = await self.db.fetch(select, user_id)
        if len(row) >= 20: raise RuntimeError(f"You have reached the limit of 20 notifications")
        return row

    async def notify_skin_check(self, user_id: int, skin_uuid: str, emoji: str, name: str) -> None:
        query = 'SELECT * FROM valorant.notifys WHERE user_id = $1 AND uuid = $2;'
        row = await self.db.fetchrow(query, user_id, skin_uuid)
        if row is not None:
            raise RuntimeError(f'{emoji} **{name}** is already in your notifys')

    async def notify_insert(self, skin_uuid: str, user_id: int, guild_id: int):
        query = 'INSERT INTO valorant.notifys(user_id, uuid, guild_id) VALUES ($1, $2, $3);'
        await self.db.execute(query, skin_uuid, user_id, guild_id)
    
    async def notify_status(self, user_id: int):
        notify_mode = await self._get_notify_mode(user_id)
        if notify_mode is None:
            query = 'UPDATE valorant.users SET notify_mode=$1 WHERE user_id = $2;'
            await self.db.execute(query, 'Spc', user_id)