# Nie jest to najlepsze rozwiązanie, ale mechanizm zegara pracującego w tle
# może się okazać przydatny w przyszłości
import asyncio
import player

class PeriodicChecker:  # klasa odpowiedzialna za sprawdzanie czy ktoś jest połączony do kanału
    def __init__(self, voice_clients):
        self.running = False
        self.task = None
        self.voice_clients = voice_clients
 
 # sprawdza czy ktoś jest połączony + czy bot sam jest połączony, jak nie to checker się sam zatrzymuje
    async def check_channel_conn(self):
        while self.running:
            try:
                for guild_id, vc in list(self.voice_clients.items()):
                    if not vc.is_connected():
                        print(f"Bot is not connected to any voice channel in guild {guild_id}. Stopping checker.")
                        await self.stop()
                        return
                    if len(vc.channel.members) == 1:
                        await vc.disconnect()
                        del self.voice_clients[guild_id]
                        await self.player.stop(guild_id)
                        print(f"Disconnected from {vc.channel.name} due to inactivity.")
            except Exception as e:
                print(f"Error in check_channel_conn: {e}")
            await asyncio.sleep(30) 

# Rozpoczyna checker i jego task
    async def start(self):
    async def start(self, player):
        if not self.running:
            self.running = True
            self.player = player
            self.task = asyncio.create_task(self.check_channel_conn())
            print("Started periodic check.")
        else:
            print("Checker already running.")

# zatrzymuje checker i jego task
    async def stop(self):
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
            print("Stopped periodic check.")
        else:
            print("Attempting to stop while checker is not running.")
