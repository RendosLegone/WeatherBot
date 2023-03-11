from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


subscribeKeyboard = InlineKeyboardBuilder()
subButton = InlineKeyboardButton(
    text="Подписаться на прогноз",
    callback_data="subButton"
)
unSubButton = InlineKeyboardButton(
    text="Отписаться от прогноза",
    callback_data="unSubButton"
)


def genSubscribeButton(newUser=True):
    if newUser:
        subscribeKeyboard.add(subButton)
    else:
        subscribeKeyboard.add(unSubButton)
    return subscribeKeyboard


