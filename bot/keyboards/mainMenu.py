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
    text="Изменить время ежедневного прогноза",
    callback_data="editTime"
)
getWeather = InlineKeyboardButton(
    text="Прогноз на завтра",
    callback_data="getWeather"
)


def genMainKeyboard(newUser=True):
    if newUser:
        mainKeyboard.add(subscribeButton)
    else:
        mainKeyboard.add(unsubscribeButton)
        mainKeyboard.add(editNotifyTime)
        mainKeyboard.add(getWeather)
    return mainKeyboard
