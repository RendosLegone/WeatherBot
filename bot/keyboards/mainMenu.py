from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


mainKeyboard = InlineKeyboardBuilder()
subscribeButton = InlineKeyboardButton(
    text="Подписаться на прогноз погоды",
    callback_data="subscribe"
)
unsubscribeButton = InlineKeyboardButton(
    text="Отписаться от прогноза погоды",
    callback_data="unsubscribe"
)
editNotifyTime = InlineKeyboardButton(
    text="Изменить время",
    callback_data="editTime"
)
getWeather = InlineKeyboardButton(
    text="Прогноз на завтра",
    callback_data="getWeather"
)
editLocation = InlineKeyboardButton(
    text="Изменить адрес",
    callback_data="editLocation"
)
buySubscription = InlineKeyboardButton(
    text="Оформить подписку",
    callback_data="buySubscription"
)


def genMainKeyboard(newUser=True):
    if newUser:
        mainKeyboard.add(subscribeButton)
    else:
        mainKeyboard.add(unsubscribeButton)
        mainKeyboard.add(editNotifyTime)
        mainKeyboard.add(getWeather)
        mainKeyboard.add(editLocation)
        mainKeyboard.add(buySubscription)
    return mainKeyboard
