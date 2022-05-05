import discord
import requests
from typing import Optional, Any
from colorthief import ColorThief
from io import BytesIO
from PIL import Image, ImageColor

def get_dominant_color(url: str) -> int:
    try:
        resp = requests.get(url)      
        out = BytesIO(resp.content)
        out.seek(0)
        icon_color = ColorThief(out).get_color(quality=1)
        icon_hex = '{:02x}{:02x}{:02x}'.format(*icon_color)
        dominant_color = int(icon_hex, 16)
        return dominant_color
    except:
        return 0xffffff

class Banner(discord.Asset): # This is our banner class. The only reason for this to add a `.color` and a `.url`.
    def __init__(self, user: discord.User, state: Any, url:str, banner_color: Any) -> None:
        self.user = user
        self.color = banner_color
        self.color_avatar:int = None
        super().__init__(state=state, url=url, key='')

    @property
    def url(self) -> Optional[str]:
        if self._url is None:
            return None
            
        return self.BASE + self._url
    
    @property
    def dominant_color(self) -> discord.File:
        img = Image.new("RGB", (256, 144), self.color)
        buffer = BytesIO()
        img.save(buffer, 'png')
        buffer.seek(0)
        f = discord.File(buffer, filename='color.png')
        return f

    @property
    def color_from_avatar(self) -> discord.File:
        avatar_url = f"https://cdn.discordapp.com/avatars/{self.user.get('id')}/{self.user.get('avatar')}.png"
        color = get_dominant_color(avatar_url)
        self.color_avatar = color
        img = Image.new("RGB", (256, 144), color)
        buffer = BytesIO()
        img.save(buffer, 'png')
        buffer.seek(0)
        f = discord.File(buffer, filename='color.png')
        return f