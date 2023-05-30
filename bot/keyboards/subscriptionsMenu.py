from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from bot.database import dbSubscriptions, UserDB, dbDiscounts

pay = InlineKeyboardButton(
    text="{0}"
         "({1}"
         " RUB)",
    callback_data="pay"
)
go_back = InlineKeyboardButton(
    text="Назад 🔙",
    callback_data="back"
)

subscriptionsButtons = [pay, go_back]


def genSubscriptionsKeyboard(user: UserDB):
    buttons = []
    subscriptions = dbSubscriptions.getSubscriptions()
    for subscription in subscriptions:
        user_discount = 0
        if user.discounts:
            user_discounts = []
            for discount in user.discounts:
                user_discounts.append(dbDiscounts.getDiscount(name=discount).amount)
            user_discount = sum(user_discounts)
        if "discount" in subscription.price:
            discount = subscription.price['discount'] + user_discount
            price = subscription.price['base'] - subscription.price['base'] / 100 * discount
        else:
            price = subscription.price['total'] - subscription.price['total'] / 100 * user_discount
        pay_button = pay.copy()
        pay_button.callback_data += f"__{subscription.name}"
        pay_button.text = pay_button.text.format(subscription.label, price)
        buttons.append(pay_button)
    buttons.append(go_back)
    return InlineKeyboardBuilder().row(*buttons, width=1)
