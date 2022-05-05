import discord
import wavelink
import os
import asyncio
import async_timeout
import re
import random
import contextlib
from discord.ext import commands
from discord import app_commands
from discord import ui
from discord import ButtonStyle
from discord import Interaction
from typing import Union, Tuple, Optional, Literal, List
from wavelink.ext import spotify
from wavelink import LavalinkException, LoadTrackError

from utils import Latte_Bot
from utils.formats import deltaconv
from utils.emojis import latte_emoji

latte_guild_id = 840379510704046151
default_guild = discord.Object(id=latte_guild_id)

LAVALINK_NODE = [
    {"host": "127.0.0.1", "port": 2333, "password": "089298", "identifier": "Lavalink"},
]

class QueueEmpty(Exception):
    """Raised when the queue is empty."""
    pass

class BotNotConnected(Exception):
    """Raised when the bot is not connected to a voice channel."""
    pass

class UserNotConnected(Exception):
    """Raised when the user is not connected to a voice channel."""
    pass

class InvalidSearch(Exception):
    """Raised when the search is invalid."""
    pass

class QueueView(ui.View):

    def __init__(self, interaction: Interaction, voice: wavelink.Player) -> None:
        super().__init__(timeout=60)
        self.interaction = interaction
        self.bot = getattr(interaction, "client", interaction._state._get_client())
        self.voice = voice 
        self.current_page = 0
        self.embeds: List[discord.Embed] = self.build_embed()
        self._update_buttons()

    def fill_items(self) -> None:
        ...
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        return False
    
    async def on_timeout(self) -> None:
        await self.interaction.edit_original_message(view=None)

    def _update_buttons(self) -> None:
        styles = {True: ButtonStyle.gray, False: ButtonStyle.blurple}
        page = self.current_page
        total_page = len(self.embeds) - 1
        self.next_page.disabled = page == total_page
        self.back_page.disabled = page == 0
        self.first_page.disabled = page == 0
        self.last_page.disabled = page == total_page
        # self.next_page.style = styles[page == total]
        # self.last_page.style = styles[page == total]
        # self.back_page.style = styles[page == 0]
        # self.first_page.style = styles[page == 0]
        if total_page == 0 and len(self.voice.queue) != 0:
            self.clear_items()

    async def show_page(self, interaction: Interaction, page_number: int) -> None:
        try:
            if page_number <= 1 and page_number != 0:
                page_number = self.current_page + page_number
            self.current_page = page_number
            self._update_buttons()
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    @ui.button(label='≪', style=ButtonStyle.grey)
    async def first_page(self, interaction: Interaction, button: ui.Button):
        await self.show_page(interaction, 0)

    @ui.button(label='Back', style=ButtonStyle.blurple)
    async def back_page(self, interaction: Interaction, button: ui.Button):
        await self.show_page(interaction, -1)

    @ui.button(label='Next', style=ButtonStyle.blurple)
    async def next_page(self, interaction: Interaction, button: ui.Button):
        await self.show_page(interaction, +1)
    
    @ui.button(label='≫', style=ButtonStyle.grey)
    async def last_page(self, interaction: Interaction, button: ui.Button):
        last = len(self.embeds) - 1
        await self.show_page(interaction, last)

    def defaut_embed(self) -> discord.Embed:
        track: wavelink.Track = self.voice.track
        embed = discord.Embed(description=f'**Now Playing:**\n```{track}```', color=self.bot.theme)
        embed.set_author(name='Music Queue')

        if len(self.voice.queue) != 0:
            embed.description += '**Upcoming Queue:**'
        # embed.set_author(name=self.interaction.user.name, icon_url=self.interaction.user.avatar)

        return embed

    def build_embed(self) -> discord.Embed:

        embeds = []
        embed = self.defaut_embed()
        total_queue: wavelink.Queue = self.voice.queue
        track: wavelink.Track = self.voice.track

        if len(total_queue) == 0:
            self.clear_items()
            if isinstance(track, wavelink.YouTubeTrack):
                self.add_item(ui.Button(label='Listen on youtube', url=track.uri, emoji=latte_emoji('youtube')))
            # if isinstance(track, wavelink.PartialTrack):
            #     self.add_item(ui.Button(label='Music URL', emoji='🎵'))
                
        count = 1
        track_queue = 1

        for track in total_queue:
            title: str = track.title
            author: discord.Member = track.author

            embed.description += f'\n{track_queue}. {title[:28]} | {author.mention}'
            if count == 5:
                embeds.append(embed)
                embed = self.defaut_embed()
                count ^= 5
            track_queue += 1
            count += 1
        
        if count > 1 or len(total_queue) == 0:
            embeds.append(embed)

        return embeds

    async def start(self) -> None:
        await self.interaction.response.send_message(embed=self.embeds[0], view=self)

class Embed(discord.Embed):
    def __init__(self, description=None, color=0xffffff, **kwargs) -> None:
        super().__init__(description=description, color=color, **kwargs)

class Music(commands.Cog):
    """Play music commands"""

    def __init__(self, bot: Latte_Bot) -> None:
        self.bot = bot
        self.loop_queue = {}
        self.loop_track = {}
        bot.loop.create_task(self.connect_nodes())
        #  self._cd = commands.CooldownMapping.from_cooldown(1.0, 60.0, commands.BucketType.user)

        # context_menu
        self.play_ctx = app_commands.ContextMenu(name='Play',callback=self.play_ctx_callback, guild_ids=[latte_guild_id])
        self.skip_ctx = app_commands.ContextMenu(name='Skip',callback=self.skip_ctx_callback, guild_ids=[latte_guild_id])
        self.shuffle_ctx = app_commands.ContextMenu(name='Shuffle',callback=self.shuffle_ctx_callback, guild_ids=[latte_guild_id])
        self.leave_ctx = app_commands.ContextMenu(name='Leave',callback=self.leave_ctx_callback, guild_ids=[latte_guild_id])
        # self.skis_ctx = app_commands.ContextMenu(name='play',callback=self.play_ctx_callback)

        # add context menu
        self.bot.tree.add_command(self.play_ctx)
        self.bot.tree.add_command(self.skip_ctx)
        self.bot.tree.add_command(self.shuffle_ctx)
        self.bot.tree.add_command(self.leave_ctx)
    
    @property
    def display_emoji(self) -> discord.Emoji:
        return self.bot.get_emoji(958861859161767987)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.play_ctx.name, type=self.play_ctx.type)
        self.bot.tree.remove_command(self.skip_ctx.name, type=self.skip_ctx.type)
        self.bot.tree.remove_command(self.shuffle_ctx.name, type=self.shuffle_ctx.type)
        self.bot.tree.remove_command(self.leave_ctx.name, type=self.leave_ctx.type)

    # def cog_check(self, ctx) -> bool:
    #     return super().cog_check(ctx)
    
    async def connect_nodes(self) -> None:
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()
        spotify_credential = getattr(
            self.bot, "spotify_credentials", {"client_id": os.getenv('spotifyID'), "client_secret": os.getenv('spotifySecret')}
        )
        for config in LAVALINK_NODE:
            try:
                node: wavelink.Node = await wavelink.NodePool.create_node(
                    bot=self.bot,
                    **config,
                    spotify_client=spotify.SpotifyClient(**spotify_credential),
                )
                print(f"Created node: {node.identifier}")
            except Exception:
                print('Failed to create node')
    
    def get_nodes(self) -> List[wavelink.Node]:
        return sorted(wavelink.NodePool._nodes.values(), key=lambda n: len(n.players))
    
    async def handle_end_stuck_exception(
        self, player: wavelink.Player, track: wavelink.Track
    ):  

        inter: Interaction = player.interaction
        voice = inter.guild.voice_client

        if voice.loop == 'TRACK':
            return await player.play(track)

        if voice.loop == 'QUEUE':
            player.queue.put(track)

        if player.queue.is_empty:
            return await voice.disconnect()

        try:
            with async_timeout.timeout(300):
                track = player.queue.get()
        except asyncio.TimeoutError:
            if not player.is_playing():
                await voice.stop()
                await voice.disconnect()
            return

        await player.play(track)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node) -> None:
        """Event fired when a node has finished connecting."""
        print(f'\n{node.identifier} is ready!')
    
    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, player: wavelink.Player, track: wavelink.Track, error) -> None:
        await self.handle_end_stuck_exception(player, track)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason) -> None:
        await self.handle_end_stuck_exception(player, track)
    
    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, player: wavelink.Player, track: wavelink.Track, threshold)-> None:
        await self.handle_end_stuck_exception(player, track)

        # inter = player.interaction
        # voice = inter.guild.voice_client
        
        # if player.queue.is_empty:
        #     return await voice.disconnect()

        # if not player.queue.is_empty:
        #     await player.play(player.queue.get())

        # next_song = voice.queue.get()
        # await voice.play(next_song)
    
        # if vc.queue.is_empty:
        #     await vc.disconnect()

        # next_track = player.queue.get()
        # await player.play(next_track)

        # await ctx.send('testing')
        
        # if all(m.bot for m in player.channel.members):
        #     return await player.disconnect()
        
        # try:
        #     with async_timeout.timeout(90):
        #             ext_track = await player.queue.get_wait()
        # except (asyncio.TimeoutError, asyncio.CancelledError):
        #     return await player.disconnect()
        # finally:
        #     with suppress(UnboundLocalError):
        #         if next_track:
        #             await player.play(next_track)
        

    async def play_music(self, search: str, interaction: Interaction) -> None:
        
        await interaction.response.defer()
        guild = interaction.guild
        user = interaction.user
        channel = interaction.channel
        #จำกัดคิวแต่ละเซิฟ

        if not user.voice:
            raise UserNotConnected("You are not connected to a voice channel.")

        # with contextlib.suppress(Exception):
        #     await guild.me.edit(deafen=True)
        
        async def search_track(query: str, Node: wavelink.Node) -> wavelink.Track:
            if decoded := spotify.decode_url(search):
                if decoded["type"] is spotify.SpotifySearchType.unusable:
                    raise InvalidSearch("Invalid search type.")
                elif decoded["type"] in (spotify.SpotifySearchType.playlist, spotify.SpotifySearchType.album):
                    async for tracks in spotify.SpotifyTrack.iterator(query=decoded["id"], type=decoded["type"], partial_tracks=True, node=Node):
                        tracks.author = user
                        voice.queue.put(tracks)
                    track = voice.queue[0]
                    if not voice.is_playing():
                        voice.loop = 'OFF'
                        await voice.play(track)
                    embed = Embed('Added the playlist to the queue.')
                    return await interaction.followup.send(embed=embed)
                elif decoded and decoded['type'] is spotify.SpotifySearchType.track:
                    track = await spotify.SpotifyTrack.search(query=decoded["id"], type=decoded["type"], return_first=True, node=Node)
            else:
                track = await wavelink.YouTubeTrack.search(query=search, return_first=True, node=Node)
            
            track.author = user
            return track

        nodes: wavelink.Node = self.get_nodes()
        track: wavelink.Track = None

        for node in nodes:
            try:
                with async_timeout.timeout(20):
                    track = await search_track(search, node)
                    break
            except asyncio.TimeoutError:
                print(f"{node.identifier} timed out")
                # wavelink.NodePool._nodes.pop(node.identifier)
                continue
            except (LavalinkException, LoadTrackError):
                continue
        
        if track is not None:

            if not interaction.client.voice_clients:
                voice: wavelink.Player = await user.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
            else:
                voice: wavelink.Player = guild.voice_client

            voice.interaction = interaction

            embed = discord.Embed(color=self.bot.theme)
            embed.set_author(name=f'{self.bot.user.name} | {channel.name}', icon_url=self.bot.user.avatar)
            embed.description = f"```{track.title}```"
            embed.set_footer(text=f'ǫᴜᴇᴜᴇ ʟᴇɴɢᴛʜ: {len(voice.queue)} | ᴅᴜʀᴀᴛɪᴏɴ: {deltaconv(track.duration)} | ᴠᴏʟᴜᴍᴇ: {voice.volume}%')

            try:
                embed.set_thumbnail(url=track.thumb)
                # if isinstance(track, wavelink.YouTubeTrack):
                #embed.set_thumbnail(url=track.thumbnail)
            except AttributeError:
                pass

            if voice.queue.is_empty and not voice.is_playing():
                voice.loop = 'OFF'
                await voice.play(track)
                await interaction.followup.send(embed=embed)            
            else:
                # embed.set_footer(text='ᴀᴅᴅ ꜱᴏɴɢ ᴛᴏ ǫᴜᴇᴜᴇ')
                await voice.queue.put_wait(track)
                await interaction.followup.send(embed=embed)

    async def skip_track(self, interaction: Interaction) -> None:
        voice: wavelink.Player = interaction.guild.voice_client

        if voice.queue.is_empty:
            raise QueueEmpty("There are no more tracks in the queue.")

        if voice and voice.is_connected():
            if not interaction.user.voice:
                raise UserNotConnected("You are not connected to a voice channel.")

            if voice.is_playing():
                await voice.stop()
                return await interaction.response.send_message(embed=Embed("Skipped the current track"))
            
            return await interaction.response.send_message(embed=Embed("No tracks in queued"))

        raise BotNotConnected("The bot is not connected to a voice channel.")

    async def leave_voice(self, interaction: Interaction) -> None:
        voice: wavelink.Player = interaction.guild.voice_client
        guild = interaction.guild
        self_bot = guild.me
        
        try:
            if voice and voice.is_connected():
                await voice.disconnect()
            else:
                await self_bot.move_to(channel=None)  
        except:
            raise BotNotConnected("The bot is not connected to a voice channel.")
        else:
            await interaction.response.send_message(embed=Embed("Disconnected from voice channel"))

    async def shuffle_queue(self, interaction: Interaction) -> None:
        voice: wavelink.Player = interaction.guild.voice_client

        if voice and voice.is_connected():
            if not interaction.user.voice:
                raise UserNotConnected("You are not connected to a voice channel.")

            voice: wavelink.Player = interaction.guild.voice_client
            random.shuffle(voice.queue._queue)
            await interaction.response.send_message(embed=Embed("Shuffled the queue"))
            return
        
        raise BotNotConnected("The bot is not connected to a voice channel.")
        
    @app_commands.command()
    @app_commands.guilds(default_guild)
    @app_commands.describe(search='Search for a song')
    async def play(self, interaction: Interaction, search:str) -> None:
        """Play music"""

        await self.play_music(search, interaction)
        
    @app_commands.command()
    @app_commands.guilds(default_guild)
    async def queue(self, interaction: Interaction) -> None:
        """Show the queue"""
        
        voice: wavelink.Player = interaction.guild.voice_client

        if not voice:
            raise BotNotConnected("The bot is not connected to a voice channel.")

        view = QueueView(interaction, voice)
        await view.start()
    
    @app_commands.command()
    @app_commands.guilds(default_guild)
    @app_commands.describe(mode='Set Queue Mode')
    async def loop(self, interaction: Interaction, mode: Literal['Track','Queue','Off']) -> None:
        """loop the track or queue"""

        voice: wavelink.Player = interaction.guild.voice_client

        if voice and voice.is_connected():
            if not interaction.user.voice:
                raise UserNotConnected()

            if mode == 'Track': content = 'Loop track'
            elif mode == 'Queue': content = 'Loop queue'
            else: content = 'Loop disabled'
            
            voice.loop = mode.upper()
            await interaction.response.send_message(embed=Embed(f"{content}"))
            return

        raise BotNotConnected()
    
    @app_commands.command()
    @app_commands.describe()
    @app_commands.guilds(default_guild)
    async def skip(self, interaction: Interaction) -> None:
        """Skip the current track"""

        await self.skip_track(interaction)
    
    @app_commands.command()
    @app_commands.guilds(default_guild)
    async def pause(self, interaction: Interaction) -> None:
        """Pause the current track"""
        voice: wavelink.Player = interaction.guild.voice_client

        if voice and voice.is_connected():
            if not interaction.user.voice:
                raise UserNotConnected("You are not connected to a voice channel.")

            if voice.is_paused():
                raise RuntimeError("Player is already paused")

            await voice.pause() 
            return await interaction.response.send_message(embed=Embed("Paused"))

        raise BotNotConnected("The bot is not connected to a voice channel.")

    @app_commands.command()
    @app_commands.guilds(default_guild)
    async def resume(self, interaction: Interaction) -> None:
        """Resume the current track"""
        voice: wavelink.Player = interaction.guild.voice_client

        if voice and voice.is_connected():
            if not interaction.user.voice:
                raise UserNotConnected("You are not connected to a voice channel.")
            
            if voice.is_paused():
                await voice.resume()
                return await interaction.response.send_message(embed=Embed("Resumed"))
            
            raise RuntimeError("Player is not paused")
        
        raise BotNotConnected("The bot is not connected to a voice channel.")
        
    @app_commands.command()
    @app_commands.guilds(default_guild)
    async def shuffle(self, interaction: Interaction) -> None:
        """Shuffle the queue"""

        await self.shuffle_queue(interaction)

    @app_commands.command()
    @app_commands.guilds(default_guild)
    @app_commands.describe(volume='Set the volume')
    async def volume(self, interaction: Interaction, volume: int) -> None:
        """Set the volume"""
        voice: wavelink.Player = interaction.guild.voice_client

        if voice and voice.is_connected():
            if not interaction.user.voice:
                raise UserNotConnected("You are not connected to a voice channel.")
            
            if volume < 0 or volume > 100:
                raise ValueError("Volume must be between 0 and 100")
            
            await voice.set_volume(volume)
            return await interaction.response.send_message(embed=Embed(f"Volume set to {volume}"))

        raise BotNotConnected("The bot is not connected to a voice channel.")
    
    @app_commands.command()
    @app_commands.guilds(default_guild)
    async def leave(self, interaction: Interaction) -> None:
        """Leave the voice channel"""
        
        await self.leave_voice(interaction)

    # @app_commands.command()
    # @app_commands.describe(song='Display lyrics for the specified song.')
    # @app_commands.guilds(default_guild)
    # async def lyrics(self, interaction: Interaction, song: str = None):
    #     """Search lyrics of the song."""

    #     await interaction.response.defer()

    #     try:
    #         access_token = 'JocfWVaPJeFQiBVM7wvszD3gCRuqTzqux_acmZ66eu-1tu92ghrnIFUhaaIhC9cv'
    #         secret_token = 'D1efjMC5SfFwUbdCoKswckfdy1zNMLq524FpzxFYHpHqxXCFi9Gdpe1oS2Eyay3tmFkngjEQ5Fe1QyLkV3T9Tw'

    #         base_url = 'https://api.genius.com'
    #         headers = {'Authorization': 'Bearer {}'.format(access_token)}

    #         search_url = base_url + "/search"
    #         data = {'q': song}

    #         r = await self.bot.session.get(search_url, headers=headers, params=data)
    #         r = await r.json()
    #         song_info = r['response']['hits'][0]['result']
    #         image = song_info['song_art_image_thumbnail_url']
    #         title = song_info['full_title']
    #         song_url = song_info['url']

    #         # Get the song lyrics
    #         # song_info = None
    #         # for hit in json["response"]["hits"]:
    #         #     if hit["result"]["primary_artist"]["name"] == artist_name:
    #         #         song_info = hit
    #         #         break

    #         # if song_info:
    #         #     song_api_path = song_info["result"]["api_path"]
    #         #     # print lyrics_from_song_api_path(song_api_path)

    #         embed = discord.Embed(title=f"Lyrics of {song}:", color=self.bot.theme)
    #         # if image is not None:
    #         #     embed.set_thumbnail(url=image)
    #         # embed.description = lyrics
    #         return await interaction.followup.send(embed=embed)
    #         # return await interaction.response.send_message(embed=embed)
    #     except Exception as e:
    #         raise RuntimeError(f'Not found lyrics of {song}')

    # CONTEXT MENU
    async def play_ctx_callback(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Play the song"""
        await self.play_music(message.content, interaction)

    async def skip_ctx_callback(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Skip the current track"""
        await self.skip_track(interaction)
    
    async def skips_ctx_callback(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Skip the current track"""
        await interaction.response.send_message('hello...')
    
    async def shuffle_ctx_callback(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Shuffle the queue"""
        await self.shuffle_queue(interaction)
    
    async def leave_ctx_callback(self, interaction: discord.Interaction, message: discord.Message) -> None:
        """Leave the voice channel"""
        await self.leave_voice(interaction)
    
async def setup(bot) -> None:
    await bot.add_cog(Music(bot))