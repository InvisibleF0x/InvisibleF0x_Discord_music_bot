import aiohttp
from tabulate import tabulate

class warframe_api:
    def __init__(self):
        self.worlds = [     # dla automacji
            ("cambionCycle", "Cambion Drift"),
            ("cetusCycle", "Cetus"),
            ("vallisCycle", "Orb Vallis")
        ]

    # określa platforme której informacje wyświetlić
    async def get_platform(self, platform, channel):
        match platform:
            case "pc":
                return "pc"
            case "ps":
                return "ps4"
            case "xb":
                return "xb1"
            case "swi":
                return "swi"
            case _:
                await channel.send("Wrong platform name, selecting default (pc)")
                return "pc"

    # wysyła zapytanie https://api.warframestat.us/{platform}
    # a następnie wypisuje informacje wszystkich open worldów
    # odwołanie do get_platform()
    async def get_world_cycles(self, channel, platform="pc"):
        platform = await self.get_platform(platform, channel)

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.warframestat.us/{platform}") as response:
                if response.status != 200:
                    #print("failed to get api")
                    await channel.send("Error getting response from Warframe API")
                    return

                data = await response.json()

        text = "```"
        for world_id, world_name in self.worlds:
            state = data.get(world_id, {}).get("state", "Unknown")
            time_left = data.get(world_id, {}).get("timeLeft", "Unknown")
            text += f"State for {world_name}: {state}\nTime until change: {time_left}\n------------------------------\n"
        text += "```"
        await channel.send(text)

    #wysyła zapytanie https://api.warframestat.us/{platform}/voidTrader
    # a następnie wypisuje informacje na temat void tredera.
    # odwołanie do get_platform()
    async def get_void_trader(self, channel, platform = "pc"):
        platform = await self.get_platform(platform, channel)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.warframestat.us/{platform}/voidTrader") as response:
                if response.status != 200:
                    #print("failed to get api")
                    print(response)
                    await channel.send("Error getting response from Warframe API")
                    return

                response = await response.json()

        text = ""

        if response.get("active") != True:
            arrival = response.get("startString")
            location = response.get("location")
            #print(f"Void treader is inactive, he will arive in: {arrival}, on {location}")
            await channel.send(f"Void treader for platform {platform} is inactive, he will arive in: `{arrival}`, on `{location}`")
        else:
            gone = response.get("endString")
            location = response.get("location")
            text = text + f"Void treader for platform {platform} is active on `{location}`, for `{gone}`." + "\n" + "His inventory:```"
            headers = ["Li.", "Item Name", "Credits", "Ducats"]
            item_list = [[]]
            for i, x in enumerate(response.get("inventory")):
                item_list.append([str(i), x.get("item"), x.get("credits"), x.get("ducats")])
            tabulated_text = tabulate(item_list, headers=headers, tablefmt="plain")
            text = text + tabulated_text
            
            if len(text) < 2000:
                await channel.send(text + "```")
            else:
                split_text = text.splitlines()
                lines_to_send = ""
                for x in split_text:
                    lines_to_send = lines_to_send + x + "\n"
                    if len(lines_to_send) > 1000:
                        await channel.send(lines_to_send + "```")
                        lines_to_send = "```"
                if len(lines_to_send) != 0 and lines_to_send != " " and lines_to_send != "```":
                    await channel.send(lines_to_send + "```")