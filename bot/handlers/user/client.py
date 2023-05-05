import datetime
from aiogram import types, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link
from bot.misc.config import configDetails
from bot.states import ClientStates
from bot.misc.util import getLoc, genPrices
from bot.misc.weather import getCertainWeather, getWeather
from bot.database import dbScheduler, dbSubscribers, UserDB, dbDiscounts, dbOldSubscribers, dbSubscriptions, dbReceipts
from bot.Scheduler import scheduler
from bot.keyboards import genMainKeyboard, genSubscriptionsKeyboard


async def menuHandler(msg: Message, subscriber: UserDB | list | bool):
    if not subscriber:
        new_user = True
        paid_subscription = 0
    elif isinstance(subscriber, list):
        new_user = "old"
        paid_subscription = dbSubscriptions.getSubscription(name=dbReceipts.getReceipt(user_id=subscriber[0])
                                                            .subscription_name).label
    else:
        new_user = False
        paid_subscription = subscriber.paid_subscription_id
    await msg.reply("Меню:", reply_markup=genMainKeyboard(new_user, paid_subscription).as_markup())


async def mainMenu(callback: CallbackQuery, state: FSMContext, bot: Bot, subscriber: UserDB | tuple | bool):
    if callback.data.split("_")[0] == "pay":
        return await subscriptions(bot, callback, subscriber)
    user_id = callback.from_user.id
    await bot.delete_message(message_id=callback.message.message_id, chat_id=user_id)
    if callback.data.split("_")[0] == "subscribe":
        await bot.send_message(
            chat_id=user_id,
            text="Укажите ваш населённый пункт(полное название или гео-метка)"
        )
        await state.set_state(ClientStates.setLoc)
    if callback.data == "unsubscribe":
        subscriber.delUser()
        await bot.send_message(
            chat_id=user_id,
            text="Вы отписались от прогноза погоды"
        )
    if callback.data == "editTime":
        await bot.send_message(
            chat_id=user_id,
            text="Во сколько вы хотите получать ежедневную рассылку?"
        )
        await state.set_state(ClientStates.editTimer)
    if callback.data == "editLocation":
        await bot.send_message(
            chat_id=user_id,
            text="Укажите ваш населённый пункт(полное название или гео-метка)"
        )
        await state.set_state(ClientStates.editLocation)
    if callback.data == "getWeather":
        date_now = datetime.datetime.now()
        location_user = subscriber.location
        weather = getWeather(location_user, -1)
        if subscriber.paid_subscription_id:
            weather += f"\n{getCertainWeather(location_user, date=[date_now.day + 1, date_now.month])}"
        await bot.send_message(
            chat_id=user_id,
            text=weather
        )
    if callback.data == "buySubscription":
        await bot.send_message(chat_id=callback.from_user.id, text="Подписки:",
                               reply_markup=genSubscriptionsKeyboard().as_markup())
    if callback.data == "resubscribe":
        await bot.send_message(
            chat_id=user_id,
            text="Укажите ваш населённый пункт(полное название или гео-метка)"
        )
        await state.set_state(ClientStates.setLoc)
    if callback.data == "getDiscount":
        link = await create_start_link(bot, str(user_id), True)
        await bot.send_message(user_id, f"Для того чтобы получить скидку нужно пригласить друга,"
                                        f"просто отправьте ему эту ссылку:\n"
                                        f"{link}")
    if callback.data == "usePromo":
        await bot.send_message(user_id, f"Отправьте промокод")
        return await state.set_state(ClientStates.usePromo)


async def usePromo(msg: Message, subscriber: UserDB | list | bool):
    promo = msg.text
    discounts = dbDiscounts.getDiscounts()
    for discount in discounts:
        if discount.trigger:
            if "promo" in discount.trigger:
                if discount.trigger["promo"] == promo:
                    if discount.limit_count:
                        if discount.limit_count == 0:
                            discount.deleteDiscount()
                            return await msg.reply(f'Промокод "{discount.label}" недействителен!')
                    if subscriber.discounts:
                        if discount.name in subscriber.discounts:
                            return await msg.reply("Вы уже использовали этот промокод!")
                    dbSubscribers.giveDiscount(subscriber.user_id, discount.name)
                    discount.decreaseLimit()
                    return await msg.reply(f'Вам выдана скидка "{discount.label}" в размере {discount.amount}%')
    return await msg.reply(f"Такого промокода не существует!")


async def subscribeStep1(msg: Message, state: FSMContext):
    await msg.reply("Укажите ваш населённый пункт(полное название или гео-метка)")
    await state.set_state(ClientStates.setLoc)


async def subscribeStep2(msg: Message, state: FSMContext):
    if msg.location:
        await state.update_data(data={"location": f"{getLoc(msg.location.latitude, msg.location.longitude)}"})
    else:
        await state.update_data(data={"location": msg.text})
    await msg.reply("Во сколько вы хотите получать ежедневный прогноз?")
    await state.set_state(ClientStates.setTimer)


async def subscribeStep3(msg: Message, state: FSMContext, bot: Bot,
                         time: str, subscriber: UserDB | tuple | bool, discounts: dict | None):
    data = await state.get_data()
    location = data["location"]
    old_user = False
    paid_subscription = None
    if isinstance(subscriber, list):
        old_user = True
        paid_subscription = dbSubscriptions.getSubscription(name=dbReceipts.getReceipt(user_id=subscriber[0])
                                                            .subscription_name).label
    dbSubscribers.addUser(msg.from_user.id, location, msg.from_user.username, time,
                          dbReceipts.getReceipt(user_id=subscriber[0]).telegram_purchase_id if old_user else None)
    if not dbScheduler.timeExist(time):
        await scheduler.addTime(time, bot)
    await msg.reply(f"""Вы подписались на ежедневный прогноз погоды!
    Адрес: {location}
    Расписание: Каждый день в {time}
    Платная подписка: {f'{paid_subscription}' if paid_subscription else 'Нет'}""")
    if discounts:
        if discounts == "abuse":
            await msg.reply("За приглашение самого себя вы получаете скидку 0% ;)")
        else:
            discount = discounts["invited"]
            discount.give_discount(msg.from_user.id)
            await msg.reply(f"Вы получаете скидку в размере {discount.amount}% {discount.label}")
            invited_from_id = discounts["invited_from_id"]
            discount = discounts["invited_from"]
            discount.give_discount(invited_from_id)
            await bot.send_message(invited_from_id, f"Вы получаете скидку в размере {discount.amount}% "
                                                    f"{discount.label}")
    if old_user:
        dbOldSubscribers.deleteUser(user_id=subscriber[0])
        return await state.clear()
    await msg.reply("Оформить платную подписку на детальный прогноз можно в /menu ;)")
    return await state.clear()


async def editLocation(msg: Message, state: FSMContext, subscriber: UserDB | tuple | bool):
    if msg.location:
        location = getLoc(msg.location.latitude, msg.location.longitude)
    else:
        location = msg.text
    subscriber.updateUser(location=location)
    await msg.reply("Ваш адрес изменён!")
    await state.clear()


async def editTime(msg: Message, state: FSMContext, bot: Bot, subscriber: UserDB | tuple | bool, time: str):
    old_time = dbSubscribers.getUser(user_id=msg.from_user.id).notify_time
    print(dbScheduler.timeExist(time))
    if not dbScheduler.timeExist(time):
        print("awdawd")
        await scheduler.addTime(time, bot)
        dbScheduler.addTime(time)
    subscriber.updateUser(notify_time=time)
    dbScheduler.decreaseCount(old_time)
    await msg.reply("Время рассылки успешно изменено!")
    await state.clear()


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    print(await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True))


async def successful_payment(msg: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = msg.successful_payment
    for k, v in payment_info:
        print(f"{k} = {v}")
    subscription = dbSubscriptions.getSubscription(name=payment_info.invoice_payload)
    date_time = datetime.datetime.now()
    dbReceipts.addReceipt(payment_info.invoice_payload, payment_info.currency, payment_info.total_amount,
                          payment_info.telegram_payment_charge_id, payment_info.provider_payment_charge_id,
                          msg.from_user.id, date_time, payment_info.shipping_option_id,
                          payment_info.order_info)
    dbSubscribers.updateUser(msg.from_user.id, paid_subscription_id=payment_info.telegram_payment_charge_id)
    await msg.answer(f"Платеж на сумму {payment_info.total_amount // 100}"
                     f"{payment_info.currency} прошел успешно!!!"
                     f'\nПодписка "{subscription.label}" до {str(date_time + subscription.period).split(".")[0]}'
                     f' подключена!')


async def start(msg: types.Message, state: FSMContext, subscriber: UserDB | None | list):
    if isinstance(subscriber, UserDB):
        return msg.reply(f"Вы уже подписаны на прогноз погоды, управление профилем -> /menu")
    if " " in msg.text:
        invited_from = msg.text.split(" ")[-1]
        print(invited_from)
        await state.update_data({"invited_from": invited_from})
    await msg.reply(
        text="Укажите ваш населённый пункт(полное название или гео-метка)"
    )
    return await state.set_state(ClientStates.setLoc)


async def subscriptions(bot: Bot, callback: CallbackQuery, subscriber: UserDB | None | list):
    if callback.data.split("__")[0] == "pay":
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        subscription_name = callback.data.split("__")[1]
        subscription = dbSubscriptions.getSubscription(name=subscription_name)
        prices = genPrices(subscriber, subscription)
        return await bot.send_invoice(chat_id=callback.from_user.id, payload=subscription_name, prices=prices,
                                      title=subscription.label, description=subscription.description,
                                      photo_url=subscription.photo_url, **configDetails)
