from telethon.sync import TelegramClient
from telethon import functions
from geopy import Nominatim

geolocator = Nominatim(user_agent="tgBotWeather")


async def get_user(username):
    async with TelegramClient("@rendoslegon", 2219729, "62f05ba3a682509353343b6e2fbd8802") as client:
        user = await client(functions.users.GetFullUserRequest(username))
        print(user)
        return user.user


def getLoc(latitude, longitude):
    return geolocator.geocode(f"{latitude},{longitude}")[0].split(",")[0]
