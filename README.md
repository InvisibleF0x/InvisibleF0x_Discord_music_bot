# Uruchamianie
Aby zadziałał należy utworzyć .env ze zmienną discord_token, pobrać biblioteki i
ffmpeg z dodaniem go jako ścieżkę/zmienną systemową.
Następnie uruchomić main.py i tyle.

potem dodam plik pobierający biblioteki i ffmpg.

### Jaka przyszłość ?
Bot jest wstępnie skończony, ma wszystkie core funkcje,
przyszłe updaty to fixy i ~może~ wprowadzenie odtwarzania ze spotify

### Czemu nie korzysta z systemu komend wbudowanego w discord ?
Bo jak masz pare botów to się nazwy komend pokrywają i się dłużej pisze,
po drugie, czje ciut nostaligii do pisania w ten sposób, jak kiedyś na fred bocie

## feature list
- granie z yt
- wyszukiwanie z yt
- Poziomy audio między filmami powinny być podobne
- dodawanie playlist (do 150 utworów na raz), każdy typ linku
- kolejka utworów i jej podgląd (domyślnie 10, do 40)
- mieszanie kolejki
- możliwość dodawanie na początek i koniec
- pomijanie (wszystko, kilka i jedno)
- pauza, ruzumpcja, stop
- wychodzi po 30s braku osób na kanale
- działa na paru serwerach jednocześnie
- informacje z warframe

## Komendy:
- #help -     displays this message
- #play -     adds a song to queue, with a yt link, musn't be blocked by age restrictions
- #playprio - adds a song to front of queue
- #playlist - adds a playlist to queue. Hard limit to 150 songs added for each call
- #pause -    pauses
- #resume -   resumes
- #skip -     skips, can take arguments: all, and number of songs to skip
- #stop -     stops music and leaves the channel (for now leaves the queue full)
- #queue -    displays the current queue with ability to select how many, 10 is defoult
- #search -   searches the phrase and displays top 5 videos
- #x -        if x is a number, will select the song form search
- #wf-state   shows day/night cycles for every open world
- #wf-baro -  shows the equipment for void trader
