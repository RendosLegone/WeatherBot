from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from bot.database import dbSubscriptions


def genSubscriptionsKeyboard():
    buttons = []
    subscriptions = dbSubscriptions.getSubscriptions()
    for subscription in subscriptions:
        if "discount" in subscription.price:
            buttons.append(InlineKeyboardButton(
                text=f"{subscription.label}"
                     f"({subscription.price['base'] - subscription.price['base']/100*subscription.price['discount']}"
                     f" RUB)",
                callback_data=f"pay__{subscription.name}"
            ))
        else:
            buttons.append(InlineKeyboardButton(
                text=f"{subscription.label}({subscription.price['total']} RUB)",
                callback_data=f"pay__{subscription.name}"
            ))
    return InlineKeyboardBuilder().row(*buttons, width=1)
