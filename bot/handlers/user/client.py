import datetime
from aiogram import types, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link, decode_payload
from bot.keyboards.mainMenu import genProfileKeyboard
from bot.misc.config import configDetails
from bot.misc.triggers import invited_trigger, invited_purchase, promo_trigger
from bot.states import ClientStates
from bot.misc.util import getLoc, genPrices
from bot.misc.weather import getCertainWeather, getWeather
from bot.database import dbScheduler, dbSubscribers, UserDB, dbDiscounts, dbOldSubscribers, dbSubscriptions, dbReceipts
from bot.Scheduler import scheduler
from bot.keyboards import genMainKeyboard, genSubscriptionsKeyboard


async def menuHandler(msg: Message, subscriber: UserDB | tuple | bool, bot: Bot):
    if not subscriber:
        new_user = True
        paid_subscription = 0
    elif isinstance(subscriber, tuple):
        new_user = "old"
        paid_subscription = dbSubscriptions.getSubscription(name=dbReceipts.getReceipt(user_id=subscriber[0])
                                                            .subscription_name).label
    else:
        new_user = False
        paid_subscription = subscriber.paid_subscription_id
    await bot.send_message(msg.from_user.id, "Меню:",
                           reply_markup=genMainKeyboard(new_user, paid_subscription).as_markup())


async def main_menu(callback: CallbackQuery, state: FSMContext, bot: Bot, subscriber: UserDB | tuple | bool):
    user_id = callback.from_user.id
    await bot.delete_message(message_id=callback.message.message_id, chat_id=user_id)
    if callback.data.split("_")[0] == "profile":
        await bot.send_chat_action(chat_id=user_id, action="typing")
        subscription_profile = "Отсутствует"
        discounts_profile = "Отсутствуют"
        if subscriber.paid_subscription_id:
            receipt = dbReceipts.getReceipt(telegram_purchase_id=subscriber.paid_subscription_id)
            paid_subscription = dbSubscriptions.getSubscription(name=receipt.subscription_name)
            subscription_datetime = receipt.date_time + paid_subscription.period
            subscription_profile = f"{paid_subscription.label} до {subscription_datetime.replace(microsecond=0)}"
        if subscriber.discounts:
            discounts = []
            discounts_profile = ""
            for discount in subscriber.discounts:
                discounts.append(dbDiscounts.getDiscount(name=discount))
            for discount in discounts:
                discounts_profile += f"{discount.label} в размере {discount.amount}%\n"
        return await bot.send_message(
            chat_id=user_id,
            text="Ваш профиль:\n"
                 f"Время ежедневного прогноза: {subscriber.notify_time}\n"
                 f"Адрес: {subscriber.location}\n"
                 f"Платная подписка: \n{subscription_profile}\n"
                 f"Скидки: {discounts_profile}\n",
            reply_markup=genProfileKeyboard().as_markup()
        )
    if callback.data == "subscribe":
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
    if callback.data == "getWeather":
        await bot.send_chat_action(callback.from_user.id, "typing")
        date_now = datetime.datetime.now()
        location_user = subscriber.location
        weather = getWeather(location_user, -1)
        if subscriber.paid_subscription_id:
            weather += f"\nПодробный прогноз(Платная подписка):" \
                       f"{getCertainWeather(location_user, date=[date_now.day + 1, date_now.month])}"
        await bot.send_message(
            chat_id=user_id,
            text=weather
        )
    if callback.data == "buySubscription":
        await bot.send_message(chat_id=callback.from_user.id, text="Подписки:",
                               reply_markup=genSubscriptionsKeyboard(subscriber).as_markup())
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
    if callback.data == "back":
        pass


async def subscriptions_menu(callback: CallbackQuery, bot: Bot, subscriber: UserDB | None | tuple):
    await bot.delete_message(message_id=callback.message.message_id, chat_id=callback.from_user.id)
    if callback.data.split("__")[0] == "pay":
        await bot.send_chat_action(callback.from_user.id, "typing")
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        subscription_name = callback.data.split("__")[1]
        subscription = dbSubscriptions.getSubscription(name=subscription_name)
        prices = genPrices(subscriber, subscription)
        return await bot.send_invoice(chat_id=callback.from_user.id, payload=subscription_name, prices=prices,
                                      title=subscription.label, description=subscription.description,
                                      photo_url=subscription.photo_url, **configDetails)
    if callback.data == "back":
        await bot.send_message(callback.from_user.id, "Меню:",
                               reply_markup=genMainKeyboard(False, subscriber.paid_subscription_id).as_markup())


async def profile_menu(callback: CallbackQuery, subscriber: UserDB, state: FSMContext, bot: Bot):
    user_id = callback.from_user.id
    await bot.delete_message(message_id=callback.message.message_id, chat_id=user_id)
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
    if callback.data == "back":
        await bot.send_message(callback.from_user.id, "Меню",
                               reply_markup=genMainKeyboard(False, subscriber.paid_subscription_id).as_markup())


async def editLocation(msg: Message, bot: Bot, state: FSMContext, subscriber: UserDB | tuple | bool):
    if msg.location:
        location = getLoc(msg.location.latitude, msg.location.longitude)
    else:
        location = msg.text
    subscriber.updateUser(location=location)
    await bot.send_chat_action(msg.from_user.id, "typing")
    await msg.reply("Ваш адрес изменён!")
    await state.clear()


async def editTime(msg: Message, state: FSMContext, bot: Bot, subscriber: UserDB | tuple | bool, time: str):
    old_time = dbSubscribers.getUser(user_id=msg.from_user.id).notify_time
    if not dbScheduler.timeExist(time):
        await scheduler.addTime(time, bot)
        dbScheduler.addTime(time)
    subscriber.updateUser(notify_time=time)
    dbScheduler.decreaseCount(old_time)
    await bot.send_chat_action(msg.from_user.id, "typing")
    await msg.reply("Время рассылки успешно изменено!")
    await state.clear()


async def usePromo(msg: Message, state: FSMContext, bot: Bot, subscriber: UserDB | tuple | bool):
    await promo_trigger(bot, subscriber, msg.text)
    return await state.clear()


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
                         time: str, subscriber: UserDB | tuple | bool):
    data = await state.get_data()
    location = data["location"]
    invited_id = data["invited_from"]
    old_user = False
    paid_subscription = None
    if isinstance(subscriber, tuple):
        old_user = True
        paid_subscription = dbSubscriptions.getSubscription(name=dbReceipts.getReceipt(user_id=subscriber[0])
                                                            .subscription_name).label
    dbSubscribers.addUser(msg.from_user.id, location, msg.from_user.first_name, time,
                          dbReceipts.getReceipt(user_id=subscriber[0]).telegram_purchase_id if old_user else None)
    if not dbScheduler.timeExist(time):
        await scheduler.addTime(time, bot)
    await bot.send_chat_action(msg.from_user.id, "typing")
    await msg.reply(f"""Вы подписались на ежедневный прогноз погоды!
    Адрес: {location}
    Расписание: Каждый день в {time}
    Платная подписка: {f'{paid_subscription}' if paid_subscription else 'Нет'}""")
    newUser = dbSubscribers.getUser(user_id=msg.from_user.id)
    if invited_id:
        await invited_trigger(bot, newUser, decode_payload(invited_id))
    if old_user:
        print("ok")
        dbOldSubscribers.deleteUser(user_id=subscriber[0])
        return await state.clear()
    await bot.send_chat_action(msg.from_user.id, "typing")
    await msg.reply("Оформить платную подписку на детальный прогноз можно в /menu ;)")
    return await state.clear()


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def successful_payment(msg: types.Message, bot: Bot):
    await bot.send_chat_action(msg.from_user.id, "typing")
    subscriber = dbSubscribers.getUser(user_id=msg.from_user.id)
    payment_info = msg.successful_payment
    subscription = dbSubscriptions.getSubscription(name=payment_info.invoice_payload)
    date_time = datetime.datetime.now()
    dbReceipts.addReceipt(payment_info.invoice_payload, payment_info.currency, payment_info.total_amount,
                          payment_info.telegram_payment_charge_id, payment_info.provider_payment_charge_id,
                          msg.from_user.id, date_time, payment_info.shipping_option_id,
                          payment_info.order_info)
    subscriber.updateUser(paid_subscription_id=payment_info.telegram_payment_charge_id)
    await bot.send_chat_action(msg.from_user.id, "typing")
    await msg.answer(f"Платеж на сумму {payment_info.total_amount // 100}"
                     f"{payment_info.currency} прошел успешно!!!"
                     f'\nПодписка "{subscription.label}" до {str(date_time + subscription.period).split(".")[0]}'
                     f' подключена!')
    if subscriber.invited_from:
        await invited_purchase(bot, subscriber)


async def start(msg: types.Message, bot: Bot, state: FSMContext, subscriber: UserDB | None | tuple):
    await bot.send_chat_action(msg.from_user.id, "typing")
    if isinstance(subscriber, UserDB):
        return msg.reply(f"Вы уже подписаны на прогноз погоды, управление профилем -> /menu")
    if " " in msg.text:
        invited_from = msg.text.split(" ")[-1]
        await state.update_data({"invited_from": invited_from})
    else:
        await state.update_data({"invited_from": None})
    await msg.reply(
        text="Укажите ваш населённый пункт(полное название или гео-метка)"
    )
    return await state.set_state(ClientStates.setLoc)

