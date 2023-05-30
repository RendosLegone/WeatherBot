from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
# 💵💳🔅❌✔⏰ 🧾🔑🔤💲⛱☁🏙🌏🌐
subscribeButton = InlineKeyboardButton(
    text="Подписаться на прогноз погоды ✔",
    callback_data="subscribe"
)
unsubscribeButton = InlineKeyboardButton(
    text="Отписаться от прогноза погоды ❌",
    callback_data="unsubscribe"
)
editNotifyTime = InlineKeyboardButton(
    text="Изменить время ⏰",
    callback_data="editTime"
)
getWeather = InlineKeyboardButton(
    text="Прогноз на завтра ☁",
    callback_data="getWeather"
)
editLocation = InlineKeyboardButton(
    text="Изменить адрес 🌐",
    callback_data="editLocation",
    request_location=True
)
buySubscription = InlineKeyboardButton(
    text="Оформить подписку 💳",
    callback_data="buySubscription"
)
resubscribe = InlineKeyboardButton(
    text="Вернуть подписку 🧾 \n\n({0})",
    callback_data="resubscribe"
)
getDiscount = InlineKeyboardButton(
    text="Получить скидку 💲",
    callback_data="getDiscount"
)
usePromo = InlineKeyboardButton(
    text="Использовать промокод 🔤",
    callback_data="usePromo"
)
profile = InlineKeyboardButton(
    text="Профиль 🔑",
    callback_data="profile"
)
go_back = InlineKeyboardButton(
    text="Назад 🔙",
    callback_data="back"
)

mainButtons = [resubscribe, subscribeButton, getWeather, getDiscount, buySubscription, profile, usePromo]
profileButtons = [editLocation, editNotifyTime, go_back]


def genMainKeyboard(new_user, paid_subscription):
    if new_user == "old":
        resubscribe.text = resubscribe.text.format(paid_subscription)
        return InlineKeyboardBuilder().add(resubscribe)
    if new_user is True:
        return InlineKeyboardBuilder().add(subscribeButton)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(getWeather, profile, width=2)
    keyboard.row(unsubscribeButton, width=1)
    keyboard.row(getDiscount, usePromo, width=2)
    if not paid_subscription:
        keyboard.row(buySubscription, width=1)
    return keyboard


def genProfileKeyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(editLocation, editNotifyTime, width=2)
    keyboard.row(go_back, width=1)
    return keyboard


def genDiscountButton(user_id):
    discountButton = InlineKeyboardButton(
        text="Подписаться на прогноз погоды",
        callback_data=f"subscribe_{user_id}"
    )
    return InlineKeyboardBuilder().add(discountButton)
