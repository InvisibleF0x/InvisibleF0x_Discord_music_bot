import yt_dlp

ytdl_search = yt_dlp.YoutubeDL({"playlistend":5})

class mock():
    def ___init___(self):
        self.search_flag = False
        self.results = []

    def format_duration(self, duration):
            minutes, seconds = divmod(duration, 60)
            return f"{minutes}:{seconds:02}"

    def search_results(self, url):
        search_result=[]
        data = ytdl_search.extract_info(url, download=False)
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

    def list_search_results(self, url):
        self.results = self.search_results(url)
        self.search_flag = True  #self
        print("Wybierz piosenkę do zagrania (#1):")
        for x in range(1,6):
            print(str(x) + "." + self.results[x-1][1] + " - " + self.format_duration(self.results[x-1][2]))

    def add_search_result_to_queue(self, x):
        if self.search_flag:
            print("Wybrano nr" + str(x) + "." + self.results[x-1][1] + " - " + self.format_duration(self.results[x-1][2]))
            #tutaj dać add_song z linkiem self.results[x-1][0]
        else:
            print("There is nothing to choose from")

mok = mock()

mok.list_search_results("https://www.youtube.com/results?search_query=szmitek+dźwig")

x = input("Wybor: ")
print(mok.add_search_result_to_queue(int(x)))

