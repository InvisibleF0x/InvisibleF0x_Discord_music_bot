import asyncio
from collections import deque
import yt_dlp
import discord
import random

yt_dl_options_playlist = {"format": "bestaudio/best", "ignoreerrors": True, "playlistend": 150}
yt_dl_options_single = {"format": "bestaudio/best", "noplaylist": True, "ignoreerrors": True, "playlistend":1}
ytdl = yt_dlp.YoutubeDL(yt_dl_options_single)
ytdl_playlist = yt_dlp.YoutubeDL(yt_dl_options_playlist)
ytdl_search = yt_dlp.YoutubeDL({"format": "bestaudio/best", "ignoreerrors": True, "playlistend": 5})
extractor_options = {"download": False}


class song_player:
    # zainicjalizowanie wszystkich zmiennych
    def __init__(self, voice_clients, ffmpeg_options):
        self.running = {}
        self.task = {}
        self.music_dequeue = {} # Przechowuje tuple (url, title, duration)
        self.voice_clients = voice_clients
        self.ffmpeg_options = ffmpeg_options
        self.current_voice_client = {}
        self.current_song_info = {}
        self.search_flag = {} # aby ignorować wiadomości #n kiedy nic nie jest wyszukiwane
        self.results = {}  # wyniki wyszukiwania tupe (url, title, duration)

    # rozpoczęcie playera i utworzenie tasku
    async def start(self, guild_id):
        if not self.running.get(guild_id):
            self.running[guild_id] = True
            self.task[guild_id] = asyncio.create_task(self.player(guild_id))
            print("Started music player.")
        else:
            print("Music player already running.")

    # zakończenie playera, skończenie tasku
    async def stop(self, guild_id):
        if self.running.get(guild_id):
            self.running[guild_id] = False
            if self.task.get(guild_id):
                self.task[guild_id].cancel()
                try:
                    await self.task[guild_id]
                except asyncio.CancelledError:
                    pass
            print("Stopped music player.")
        else:
            print("Attempting to stop while music player is not running.")

    # pomijanie określanej liczby utworów 
    async def skip(self, channel, one=False, all=False, num=1):
        guild_id = channel.guild.id
        if self.running.get(guild_id):
            if all:
                self.music_dequeue[guild_id].clear()
                if self.current_voice_client.get(guild_id) and self.current_voice_client[guild_id].is_playing():
                    self.current_voice_client[guild_id].stop()
                    print("Stopped current song.")
                    await channel.send("Stopped all songs.")
                    self.current_song_info[guild_id] = None
            elif one:
                if self.current_voice_client.get(guild_id) and (self.current_voice_client[guild_id].is_playing() or self.current_voice_client[guild_id].is_paused()):
                    self.current_voice_client[guild_id].stop()
                    print("Skipped current song.")
                    await channel.send("Skipped current song.")
                    self.current_song_info[guild_id] = None
                else:
                    print("No song is currently playing.")
            elif num > 0:
                for _ in range(num - 1):
                    if self.music_dequeue[guild_id]:
                        self.music_dequeue[guild_id].popleft()
                if self.current_voice_client.get(guild_id) and self.current_voice_client[guild_id].is_playing():
                    self.current_voice_client[guild_id].stop()
                    print(f"Skipped {num} songs.")
                    await channel.send(f"Skipped {num} songs.")
                    self.current_song_info[guild_id] = None
            else:
                print("Invalid skip parameters.")

    # dodaje piosenkę do kolejki na koniec
    # odwołanie do prepare_song() i format_duration()
    async def add_song(self, channel, url):
        guild_id = channel.guild.id
        try:
            song_url, title, duration = await self.prepare_song(url, channel)
            if song_url:
                if guild_id not in self.music_dequeue:
                    self.music_dequeue[guild_id] = deque()
                self.music_dequeue[guild_id].append((song_url, title, duration))
                print(f"Added song to queue: {title} - {self.format_duration(duration)}")
                await channel.send(f"Added song to queue: {title} - {self.format_duration(duration)}")
        except Exception as e:
            print(f"Error adding song to queue: {e}")

    # dodaje piosenkę do kolejki na początek
    # odwołanie do prepare_song() i format_duration()
    async def add_song_prio(self, channel, url):
        guild_id = channel.guild.id
        try:
            song_url, title, duration = await self.prepare_song(url, channel)
            if song_url:
                if guild_id not in self.music_dequeue:
                    self.music_dequeue[guild_id] = deque()
                self.music_dequeue[guild_id].appendleft((song_url, title, duration))
                print(f"Added song to the front of the queue: {title} - {self.format_duration(duration)}")
                await channel.send(f"Added song to the front of the queue: {title} - {self.format_duration(duration)}")
        except Exception as e:
            print(f"Error adding song to queue: {e}")

    # przygotowanie piosenki aby dodać do kolejki.
    # zwraca url, tytół i długość
    async def prepare_song(self, url, channel):
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            return data['url'], data.get('title', 'Unknown'), data.get('duration', 0)
        except Exception as e:
            print(f"Error preparing song: {e}")
            await channel.send("Unable to play song, this can be coused by region block and age restrictions")
            return None, None, None

    # dodawanie playlisty do kolejki
    # odwołanie do prepare_playlist()
    async def add_playlist_to_queue(self, channel, url):
        guild_id = channel.guild.id
        try:
            await self.prepare_playlist(channel, guild_id, url)
        except Exception as e:
            print(f"Error adding playlist to queue: {e}")

    # przygotowywuje playliste, pierwsza piosenka jako pierwsza,
    # najpierw ytdl pobiera wszystko, i potem dopiero jest dodawane
    # odwołanie do format_duration()
    async def prepare_playlist(self, channel, guild_id, url):
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl_playlist.extract_info(url, download=False))

            if 'entries' in data:
                first_entry = True  # flaga oznaczająca pierwszą piosenkę
                for entry in data['entries']:
                    if entry:
                        song_url = entry.get('url')
                        title = entry.get('title', 'Unknown')
                        duration = entry.get('duration', 0)

                        if song_url and title:  # sprawzenie czy piosenka ma wszystkie informacje (dla przypadku gdy jest zablokowana, informacje będą niedostępne)
                            if not first_entry or self.current_song_info[guild_id][0] != title: #zapobieganie dodaniu 1 piosenki 2 razy
                                if guild_id not in self.music_dequeue:
                                    self.music_dequeue[guild_id] = deque()
                                self.music_dequeue[guild_id].append((song_url, title, duration))
                                print(f"Added song to queue: {title} - {self.format_duration(duration)}")
                                await channel.send(f"Added song to queue: {title} - {self.format_duration(duration)}")
                                first_entry = False
                            else:
                                print(f"Song already in queue: {title}")
                                first_entry = False  # to zawsze się odpala przy pierwszej piosence
                        else:
                            print("Skipping invalid entry in playlist")
                    else:
                        print("Skipping None entry in playlist")

        except Exception as e:
            print(f"Error preparing playlist: {e}")

    # wyświetla rezultaty wyszukiwania
    # odwołanie do format_duration() i search_results()
    async def list_search_results(self, query, channel):
        guild_id = channel.guild.id
        message = "```"
        self.results[guild_id] = await self.search_results(query)
        self.search_flag[guild_id] = True
        print("Wybierz piosenkę do zagrania (#1):")
        await channel.send("Wybierz piosenkę do zagrania (#1):")
        for x in range(1, 6):
            print(str(x) + ". " + self.results[guild_id][x - 1][1] + " - " + self.format_duration(self.results[guild_id][x - 1][2]))
            message = message + str(x) + ". " + self.results[guild_id][x - 1][1] + " - " + self.format_duration(self.results[guild_id][x - 1][2]) + "\n"
        message = message + "```"
        await channel.send(message)

    # przygotowywuje do wyświetlenia rezultat wyszukiwania
    async def search_results(self, query):
        search_result = []
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl_search.extract_info(f"ytsearch5:{query}", download=False))
        if 'entries' in data:
            for entry in data['entries']:
                if entry:
                    song_url = entry.get('webpage_url')
                    title = entry.get('title', 'Unknown')
                    duration = entry.get('duration', 0)

                    if title:
                        search_result.append((song_url, title, duration))
                    else:
                        print("Skipping invalid search result")
        return search_result
    
    # przekazuje wybraną piosenkę z wyszukiwania do add_song()
    async def add_search_result_to_queue(self, x, channel):
        guild_id = channel.guild.id
        if self.search_flag.get(guild_id):
            await self.add_song(channel, self.results[guild_id][x - 1][0])
            self.search_flag[guild_id] = False
        else:
            print("There is nothing to choose from")
            await channel.send("There is nothing to choose from")

    # metoda która rozpoczyna się przy starcie, gdy piosenka jest w kolejce
    # odtwarza ją używając ffmpegOpusAudio. Również zapamiętuje dane piosenki
    # granej, bo wyciąga informacje popem
    # odwołanie do format_duration()
    async def player(self, guild_id):
        while self.running.get(guild_id):
            if self.music_dequeue.get(guild_id) and guild_id in self.voice_clients:
                song_url, title, duration = self.music_dequeue[guild_id].popleft()
                try:
                    player = discord.FFmpegOpusAudio(song_url, **self.ffmpeg_options)
                    self.current_voice_client[guild_id] = self.voice_clients[guild_id]
                    self.current_voice_client[guild_id].play(player)
                    print("Now playing: " + title)
                    self.current_song_info[guild_id] = (title, duration)
                    while self.current_voice_client[guild_id].is_playing() or self.current_voice_client[guild_id].is_paused():
                        await asyncio.sleep(1)
                except Exception as e:
                    print(f"Error playing song: {e}")
            else:
                await asyncio.sleep(1)

    #pauzje
    async def pause(self, channel):
        guild_id = channel.guild.id
        if self.running.get(guild_id):
            if self.current_voice_client.get(guild_id) and self.current_voice_client[guild_id].is_playing():
                self.current_voice_client[guild_id].pause()
                print("Paused current song.")
                await channel.send("Paused current song.")
            else:
                print("No song is currently playing.")
                await channel.send("No song is currently playing.")

    #rezumuje
    async def resume(self, channel):
        guild_id = channel.guild.id
        if self.running.get(guild_id):
            if self.current_voice_client.get(guild_id) and self.current_voice_client[guild_id].is_paused():
                self.current_voice_client[guild_id].resume()
                print("Resumed current song.")
                await channel.send("Resumed current song.")
            else:
                print("No song is currently paused.")
                await channel.send("No song is currently paused.")

    # wyświetla od 10 do 40 utworów w kolejce i pokazuje też ich liczbe in total
    # odwołanie do format_duration()
    async def display_queue(self, x, channel):
        if x <= 0:
            x = 10
        if x > 40:
            x = 40
        guild_id = channel.guild.id
        if guild_id in self.music_dequeue and self.music_dequeue[guild_id]:
            queue_list = list(self.music_dequeue[guild_id])
            message = "Current queue:\n```"
            for i, (song_url, title, duration) in enumerate(queue_list, start=1, end=x):
                message += f"{i}. {title} - {self.format_duration(duration)}\n"
            message += "```"
            await channel.send(message)
        else:
            await channel.send("The queue is empty.")

    # użtwa random.shuffle gdy jest więcej niż 1 piosenka żeby zshuflować deque
    async def shuffle_queue(self, channel):
        guild_id = channel.guild.id
        if guild_id in self.music_dequeue and self.music_dequeue[guild_id]:
            random.shuffle(self.music_dequeue[guild_id])
            await channel.send("Shuffled the queue.")
        else:
            await channel.send("The queue is empty.")


    @staticmethod
    def format_duration(duration):
        minutes, seconds = divmod(duration, 60)
        return f"{minutes:02d}:{seconds:02d}"