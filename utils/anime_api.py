import discord
from discord import Interaction, ButtonStyle, ui
from typing import Union, Awaitable, Optional, List, Dict, Any, Literal
from utils.view import ViewAuthor

def IM_URL(tag: str) -> str:
    if tag.startswith('Waifu'): tag = 'waifu'
    build_url = f'https://api.waifu.im/random/?selected_tags={tag.lower()}'
    return build_url

def PISC_URL(type: str, tag: str) -> str:
    if tag.startswith('Waifu'): tag = 'waifu'
    build_url = f'https://api.waifu.pics/{type}/{tag.lower()}'
    return build_url

# PISC_SFW = ['Awoo','Bite', 'Blush', 'Bonk', 'Bully', 
#     'Cringe', 'Cry', 'Cuddle','Dance', 'Glomp', 
#     'Handhold', 'Happy', 'Highfive', 'Hug', 'Kick',
#     'Kill', 'Kiss', 'Lick', 'Megumin', 'Neko',
#     'Nom', 'Pat', 'Poke', 'Shinobu', 'Slap',
#     'Smile', 'Smug', 'Waifu', 'Wave', 'Wink', 'Yeet']

# PISC_NSFW = ['Waifu', 'Neko', 'Trap', 'Blowjob']

# IM_SFW = ['Uniform', 'Maid', 'Waifu', 'Marin-kitagawa', 'Mori-calliope', 'Raiden-shogun', 'Selfies', 'Oppai']

# IM_NSFW = ['Ass', 'Hentai', 'Milf', 'Oral', 'Paizuri', 'Ecchi', 'Ero']

class WAIFU_IM_VIEW(ViewAuthor):
    def __init__(self, interaction: Interaction, url: str):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.bot = getattr(interaction, "client", interaction._state._get_client())
        self.url = url
        self.image_url = ''
        self.source_url = ''

    @ui.button(label='▶', style=ButtonStyle.blurple)
    async def button_api(self, interaction: Interaction, button: ui.Button):
        embed = await self.refresh_embed()
        self.refresh_button()

        if embed:
            await interaction.response.edit_message(embed=embed, view=self)
    
    @ui.button(emoji="❤️", style=ButtonStyle.blurple)
    async def disable_all_button(self, interaction: Interaction, button: ui.Button):
        await self.on_timeout()

    def image_url_button(self) -> None:
        self.add_item(ui.Button(label='Image URL', url=self.image_url))
    
    def source_url_button(self) -> None:
        self.add_item(ui.Button(label='Source URL', url=self.source_url))
    
    def api_site(self) -> None:
        self.add_item(ui.Button(label='API site', url="https://waifu.im/"))

    async def on_timeout(self) -> None:
        self.clear_items()
        self.image_url_button()
        self.source_url_button()
        self.api_site()
        try:
            await self.interaction.edit_original_message(view=self)
        except Exception as e:
            print(e)
    
    def refresh_button(self) -> None:
        for items in self.children:
            if items.label == "Image URL":
                self.remove_item(item=items)
                self.image_url_button()
    
    async def refresh_embed(self) -> Optional[discord.Embed]:
        image = await self.get_image()
        if image is not None:
            name = image['name']
            color = image['color']
            url = image['url']
            source_url = image['source']
            self.image_url = url
            self.source_url = source_url

            embed = self.build_embed(name, color, url, source_url)
            return embed

    def build_embed(self, name:str, color, image_url:str, source_url:str) -> discord.Embed:
        embed = discord.Embed(color=int(color))
        embed.set_author(name=name.capitalize())
        if source_url is not None:
            embed.set_author(name=name.capitalize(), url=source_url)
        embed.set_image(url=image_url)
        embed.set_footer(text="Powered by waifu.im")
        return embed

    async def get_image(self) -> Optional[Dict]:
        source = None
        r = await self.bot.session.get(self.url)
        if r.status == 200:        
            data = await r.json()
            name = data.get('images')[0].get('tags')[0].get('name')
            dominant_color = str(data.get('images')[0].get('dominant_color')).replace('#', '')
            color = int(dominant_color, 16)
            image_url = data.get('images')[0].get('url')
            source_url = data.get('images')[0].get('source')
            
            source = {'name': name, 'url': image_url, 'color': color, 'source': source_url}

        return source

    async def main_embed(self) -> Optional[discord.Embed]:
        source = await self.get_image()
        if source is not None:
            name = source['name']
            color = source['color']
            url = source['url']
            source_url = source['source']
            self.image_url = url
            self.source_url = source_url
    
            embed = self.build_embed(name, color, url, source_url)
            return embed

    async def start(self):
        embed = await self.main_embed()
        self.image_url_button()
        await self.interaction.response.send_message(embed=embed, view=self)

class WAIFU_PISC_VIEW(ViewAuthor):
    def __init__(self, interaction: Interaction, title: str, url: str):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.bot = getattr(interaction, "client", interaction._state._get_client())
        self.title: str = title
        self.url: str = url
        self.image_url: str = ''

    @ui.button(label='▶', style=ButtonStyle.blurple)
    async def button_api(self, interaction: Interaction, button: ui.Button):
        embed = await self.refresh_embed()
        self.refresh_button()
        if embed is not None:
            await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(emoji="❤️", style=ButtonStyle.blurple)
    async def disable_all_button(self, interaction: Interaction, button: ui.Button):
        await self.on_timeout()
        self.stop()

    def image_url_button(self) -> None:
        self.add_item(ui.Button(label='Image URL', url=self.image_url))

    def api_site(self) -> None:
        self.add_item(ui.Button(label='API site', url='https://waifu.pics/'))

    async def on_timeout(self) -> None:
        self.clear_items()
        self.image_url_button()
        self.api_site()
        try:
            await self.interaction.edit_original_message(view=self)
        except Exception as e:
            print(e)
        
    def refresh_button(self) -> None:
        for items in self.children:
            if items.label == "Image URL":
                self.remove_item(item=items)
                self.image_url_button()

    async def get_image(self) -> str:
        image_url = None
        r = await self.bot.session.get(self.url)
        if r.status == 200:
            data = await r.json()
            image_url = data["url"]
        return image_url

    def build_embed(self, image_url: str) -> discord.Embed:
        embed = discord.Embed(color=0xffffff)
        embed.set_author(name=self.title.capitalize(), url=image_url)
        embed.set_image(url=image_url)
        embed.set_footer(text="Powered by waifu.pisc")
        return embed

    async def refresh_embed(self) -> Optional[discord.Embed]:
        image_url = await self.get_image()
        if image_url is not None:
            self.image_url = image_url
            embed = self.build_embed(image_url)
            return embed

    async def start(self) -> Awaitable[None]:
        image_url = await self.get_image()
        if image_url is not None:
            self.image_url = image_url
            embed = self.build_embed(image_url)
            self.image_url_button()
            await self.interaction.response.send_message(embed=embed, view=self)