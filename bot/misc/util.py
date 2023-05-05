from telethon.sync import TelegramClient
from telethon import functions
from geopy import Nominatim
from aiogram.types import LabeledPrice

from bot.database import UserDB, PaidSubscriptionDB, dbDiscounts

geolocator = Nominatim(user_agent="tgBotWeather")


async def get_user(username):
    async with TelegramClient("@rendoslegon", 2219729, "62f05ba3a682509353343b6e2fbd8802") as client:
        user = await client(functions.users.GetFullUserRequest(username))
        return user.user


def getLoc(latitude, longitude):
    return geolocator.geocode(f"{latitude},{longitude}")[0].split(",")[0]


def genPrices(subscriber: UserDB, paid_subscription: PaidSubscriptionDB) -> list:
    prices = []
    if "discount" in paid_subscription.price:
        prices.append(LabeledPrice(
            amount=paid_subscription.price["base"] * 100,
            label='Цена без скидки'
        ))
        prices.append(LabeledPrice(
            amount=-paid_subscription.price["base"] * paid_subscription.price["discount"],
            label=f'Скидка в размере {paid_subscription.price["discount"]}%'
        ))
    else:
        prices.append(LabeledPrice(
            amount=paid_subscription.price["total"] * 100,
            label='Цена'
        ))
    if subscriber.discounts:
        for discount in subscriber.discounts:
            discount_db = dbDiscounts.getDiscount(name=discount)
            if "base" in paid_subscription.price:
                price = paid_subscription.price["base"]
            else:
                price = paid_subscription.price["total"]
            prices.append(LabeledPrice(
                amount=-price * discount_db.amount,
                label=f'Скидка {discount_db.label} в размере {discount_db.amount}%')
            )
    return prices
