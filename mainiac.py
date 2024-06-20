import discord
import os
import re
from checker import PeriodicChecker
from player import song_player
from warframe_requests import warframe_api
import yt_dlp
from dotenv import load_dotenv

# if client gets supplied with link to playlist and not first item, it changes
# it to be able to perform seamless loading
def get_first_playlist_item_url(playlist_url):
    ydl_opts = {
        'quiet': True,
        'noplaylist': False,
        'force_generic_extractor': True,
        'extract_flat': True,
        'extractor_args': {
            'youtube': {
                'playlist_items': None
            }
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(playlist_url, download=False)
        playlist_id=playlist_url
        playlist_id= playlist_id[38:]
        if 'entries' in info_dict:
            first_entry = info_dict['entries'][0]
            if first_entry:
                playlist_item_url = first_entry.get('url')
                if playlist_item_url:
                    return playlist_item_url+"&list="+playlist_id+"&index=1"
    
    return None

def run_bot():
    # setup klienta discord
    load_dotenv()
    TOKEN = os.getenv('discord_token')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    # setup ffmpeg, yt_dlp, zmiennych i klas lokalnych
    voice_clients = {}
    checkers = {}
    # te opcje zapewniają że nie powinien przestawać odtwarzać losowo i w teori głośność każdego video będzie podobna
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -af loudnorm=I=-16:LRA=11:TP=-1.5'}   
    player = song_player(voice_clients, ffmpeg_options)
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)
    warframe_request = warframe_api()

    #odpowiedź na gowość klienta
    @client.event
    async def on_ready():
        print(f'{client.user} napierdala')

    # Odpowiedzi na wiadomości na czacie
    @client.event
    async def on_message(message):  # bot sprawdza każdą wiadomość czy nie zaczyna się od komendy
        nonlocal checkers
        nonlocal voice_clients

        # dodaje nową piosenkę na koniec. 
        # Odwołanie do song_player.add_song(), song_player.start() i checker.start()
        # gdy dostaje link do playlisty, ładuje tylko 1 piosenkę, celowo.
        if message.content.startswith("#play"):
            try:
                if message.author.voice is None:
                    await message.channel.send("You are not connected to a voice channel.")
                    return
                
                voice_client = await message.author.voice.channel.connect()  # sprawdza czy autor jest na kanale, jak jest to dołącza
                voice_clients[voice_client.guild.id] = voice_client  # dodanie instancji bota do listy
                checker = PeriodicChecker(voice_clients)
                await checker.start(player)
                checkers[message.guild.id] = checker

            except Exception as e:
                print(e)

            try:
                url = message.content.split()[1]  # oddzielenie adresu url od komendy
                if "playlist" in url:
                    url = get_first_playlist_item_url(url)
                await player.start(message.guild.id)
                await player.add_song(message.channel,url)
            except Exception as e:
                print(e)

        # dodaje nową piosenkę na początek.
        # Odwołanie do song_player.add_song(), song_player.start() i checker.start()
        # gdy dostaje link do playlisty, ładuje tylko 1 piosenkę, celowo.
        if message.content.startswith("#playprio"):
            try:
                if message.author.voice is None:
                    await message.channel.send("You are not connected to a voice channel.")
                    return
                
                voice_client = await message.author.voice.channel.connect()  # sprawdza czy autor jest na kanale, jak jest to dołącza
                voice_clients[voice_client.guild.id] = voice_client  # dodanie instancji bota do listy
                checker = PeriodicChecker(voice_clients)
                await checker.start(player)
                checkers = [voice_client.guild.id] = checker

            except Exception as e:
                print(e)
            
            try:
                url = message.content.split()[1]  # oddzielenie adresu url od komendy
                await player.start(message.guild.id)
                await player.add_song_prio(message.channel,url)
            except Exception as e:
                print(e)

        # dodaje do 150 utworów z playlisty. 
        # Odwołanie do song_player.add_playlist_to_queue() <-- ZMIEŃIĆ NAZWE, song_player.start() i checker.start() 
        # seamles loading bo #playlist wywołuje też play XDDD, ale to git
        #! odtwarzanie z linku do playlisty a nie 1 utworu psuje niewidoczne ładowanie
        if message.content.startswith("#playlist"):
            try:
                if message.author.voice is None:
                    await message.channel.send("You are not connected to a voice channel.")
                    return
                
                voice_client = await message.author.voice.channel.connect()  # sprawdza czy autor jest na kanale, jak jest to dołącza
                voice_clients[voice_client.guild.id] = voice_client  # dodanie instancji bota do listy
                checker = PeriodicChecker(voice_clients)
                await checker.start(player)
                checkers = [voice_client.guild.id] = checker

            except Exception as e:
                print(e)
            
            try:
                url = message.content.split()[1]  # oddzielenie adresu url od komendy
                await player.start(message.guild.id)
                await player.add_playlist_to_queue(message.channel,url)
            except Exception as e:
                print(e)

        # wyszukuje top 5 filmów na yt z frazy
        # odwołanie do player.list_search_resoults()
        if message.content.startswith("#search"):
            try:
                if message.author.voice is None:
                    await message.channel.send("You are not connected to a voice channel.")
                    return
                
                voice_client = await message.author.voice.channel.connect()  # sprawdza czy autor jest na kanale, jak jest to dołącza
                voice_clients[voice_client.guild.id] = voice_client  # dodanie instancji bota do listy
                checker = PeriodicChecker(voice_clients)
                await checker.start(player)
                checkers = [voice_client.guild.id] = checker

            except Exception as e:
                print(e)
            
            try:
                query = ' '.join(message.content.split()[1:])   #wszystko po komendzie do 1 stringa
                await player.start(message.guild.id)
                await player.list_search_results(query,message.channel)
            except Exception as e:
                print(e)

        # wybór piosenki po wyszukaniu
        # odwołanie do add_search_result_to_queue()
        if re.match(r"#\d$", message.content):
            try:
                x = int(message.content[1])
                if 1 <= x <=5:
                    await player.add_search_result_to_queue(x, message.channel)
                else:
                    await message.channel.send("Wrong index, select (1-5)")
            except Exception as e:
                print(e)

        # pauzuje odtwarzacz.
        # odwołanie do song_player.pause()
        if message.content.startswith("#pause"):
            try:
                await player.pause(message.channel)
            except Exception as e:
                print(e)

        # wznawia odtwarzacz
        # odwołanie do song_player.resume()
        if message.content.startswith("#resume"):
            try:
                await player.resume(message.channel)
            except Exception as e:
                print(e)

        # pomija określoną ilość utworów. 
        # Odwołanie do song_player.skip()
        #! brak wiadomości o złym argumencie z instrukcjami, warto by było dodać
        if message.content.startswith('#skip'):
            cut_message = message.content.split()
            try:
                if len(cut_message) == 1:
                    await player.skip(message.channel,1,0,0)
                elif cut_message[1] == "all":
                    await player.skip(message.channel,0,1,0)
                else:
                    await player.skip(message.channel,0,0,int(cut_message[1]))
            except Exception as e:
                print(e)

        # wyświetla kolejkę utworów z ich liczbą. 
        # Odwołanie do song_player.display_queue()
        # przyjmuje domyślnie 10, przyjmuje argument z liczbą do max 40
        if message.content.startswith("#queue"):
            try:
                cut_message = message.content.split()
                if len(cut_message) == 1:
                    await player.display_queue(0, message.channel)
                else:
                    await player.display_queue(int(cut_message[1]), message.channel)
            except Exception as e:
                print(e)

        # miesza aktualne piosenki w kolejce. 
        # Odwołanie do song_player.shuffle()
        if message.content.startswith("#shuffle"):
            try:
                await player.shuffle_queue(message.channel)
            except Exception as e:
                print(e)

        # zatrzymuje odtwarzanie, stopuje playera i checkera. 
        # Odwołanie do checker.stop() i song_player.stop()
        if message.content.startswith("#stop"):
            try:
                if message.guild.id in voice_clients:
                    await player.stop(message.guild.id)     # ^ ale playera
                    await checkers[message.guild.id].stop()    # zatrzymanie licznika żeby nie obciążał niepotrzebnie
                else:
                    await message.channel.send("No bot connected")
            except Exception as e:
                print(e)

        # wypisuje obecne cykle w warframe używając api
        # odwołanie do warframe_requests.get_word_cycles()
        if message.content.startswith("#wf-state"):
            try:
                if len(message.content.split()) > 1:
                    await warframe_request.get_world_cycles(message.channel, message.content.split()[1])
                else:
                    await warframe_request.get_world_cycles(message.channel)
            except Exception  as e:
                print(e)

        # wypisuje informacje na temat void tradera w wargrame używając api
        # odwołanie do warframe_requests.get_void_trader
        if message.content.startswith("#wf-baro"):
            try:
                if len(message.content.split()) > 1:
                    await warframe_request.get_void_trader(message.channel, message.content.split()[1])
                else:
                    await warframe_request.get_void_trader(message.channel)
            except Exception  as e:
                print(e)

        # wyświetla liste komend
        if message.content.startswith("#help"):
            text =   '''Guten morgen frojlajns
Ich: bin; du: bist; er, sie: es;
```#help -     displays this message
#play -     adds a song to queue, with a yt link, musn't be blocked by age restrictions
#playprio - adds a song to front of queue
#playlist - adds a playlist to queue. Hard limit to 150 songs added for each call
#pause -    pauses
#resume -   resumes
#skip -     skips, can take arguments: all, and number of songs to skip
#stop -     stops music and leaves the channel (for now leaves the queue full)
#queue -    displays the current queue with ability to select how many, 10 is defoult
#search -   searches the phrase and displays top 5 videos
#x -        if x is a number, will select the song form search

For wf commands add platform (pc, xb, ps, swi), or leave empty - defoult is pc
#wf-state - shows day/night cycles for every open world
#wf-baro -  shows the equipment for void trader```Fur die minuten, das ist alles.
Oder neue functionen bist creationen'''
            await message.channel.send(text)

    # uruchomienie klienta            
    client.run(TOKEN)
