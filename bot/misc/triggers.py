from aiogram import Bot
from bot.database import UserDB, dbSubscribers, dbDiscounts


async def invited_trigger(bot: Bot, user: UserDB, invited_id):
    if user.user_id == invited_id:
        return await bot.send_message(user.user_id, "За приглашение самого себя вы получаете скидку 0% ;)")
    discount_invited = dbDiscounts.getDiscount(name="invited")
    user.giveDiscount("invited")
    await bot.send_message(chat_id=user.user_id, text=f"Вы получаете скидку {discount_invited.label} "
                                                      f"в размере {discount_invited.amount}%")
    invited_user = dbSubscribers.getUser(user_id=invited_id)
    if invited_user:
        if "inviting_1" not in invited_user.discounts:
            invited_user.giveDiscount("inviting_1")
            discount = dbDiscounts.getDiscount(name="inviting_1")
        else:
            discount = dbDiscounts.getDiscount(name="inviting_5")
            amount_invited = len(dbSubscribers.getUsers(invited_from=invited_id))
            if amount_invited != 5:
                return await bot.send_message(invited_id, f"У вас новый реферал!\n"
                                                          f"Число рефералов: {amount_invited}")
            invited_user.removeDiscount("inviting_1")
            invited_user.giveDiscount("inviting_5")
        await bot.send_message(chat_id=user.user_id, text=f"Вы получаете скидку {discount.label} "
                                                          f"в размере {discount.amount}%")


async def invited_purchase(bot: Bot, user: UserDB):
    invited_from_id = user.invited_from
    invited_from_user = dbSubscribers.getUser(user_id=invited_from_id)
    if invited_from_user:
        if "inviting_with_purchase" not in invited_from_user.discounts:
            invited_from_user.giveDiscount("inviting_with_purchase")
            discount_invited = dbDiscounts.getDiscount("inviting_with_purchase")
            return await bot.send_message(chat_id=invited_from_id, text=f"Вы получаете скидку {discount_invited.label} "
                                                                        f"в размере {discount_invited.amount}%")


async def promo_trigger(bot: Bot, user: UserDB, promo: str):
    discounts = dbDiscounts.getDiscounts()
    for discount in discounts:
        if "promo" in discount.trigger:
            if promo == discount.trigger["promo"] and discount.name not in user.discounts:
                await bot.send_message(user.user_id, f'Вам выдана скидка "{discount.label}" '
                                                     f'в размере {discount.amount}%')
                user.giveDiscount(discount.name)
                return discount.decreaseLimit()
            return await bot.send_message(user.user_id, "Вы уже использовали этот промокод")
    return await bot.send_message(user.user_id, "Промокод недействителен или его не существует")

triggers = {"invited": invited_trigger, "inviting_with_purchase": invited_purchase}
