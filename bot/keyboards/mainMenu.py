from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

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
    callback_data="editLocation",
    request_location=True
)
buySubscription = InlineKeyboardButton(
    text="Оформить подписку",
    callback_data="buySubscription"
)
resubscribe = InlineKeyboardButton(
    text="Вернуть подписку\n({0})",
    callback_data="resubscribe"
)
getDiscount = InlineKeyboardButton(
    text="Получить скидку",
    callback_data="getDiscount"
)


def genMainKeyboard(new_user, paid_subscription):
    if new_user == "old":
        resubscribe.text = resubscribe.text.format(paid_subscription)
        return InlineKeyboardBuilder().add(resubscribe)
    if new_user is True:
        return InlineKeyboardBuilder().add(subscribeButton)
    listButtons = [unsubscribeButton, editLocation, editNotifyTime, getWeather, getDiscount]
    if paid_subscription == 0:
        listButtons.append(buySubscription)
    return InlineKeyboardBuilder().row(*listButtons, width=1)


def genDiscountButton(user_id):
    discountButton = InlineKeyboardButton(
        text="Подписаться на прогноз погоды",
        callback_data=f"subscribe_{user_id}"
    )
    return InlineKeyboardBuilder().add(discountButton)
