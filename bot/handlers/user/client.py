import datetime
from aiogram import types, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link, decode_payload
from bot.states import ClientStates
from bot.misc.util import getLoc
from bot.misc.weather import getCertainWeather, getWeather
from bot.database import dbScheduler, dbSubscribers, UserDB, dbDiscounts, dbOldSubscribers
from bot.Scheduler import scheduler
from bot.keyboards import genMainKeyboard
from bot.misc.config import configPrice, configDetails


async def menuHandler(msg: Message, subscriber: UserDB | list | bool):
    if not subscriber:
        newUser = True
        paid_subscription = 0
    elif isinstance(subscriber, list):
        newUser = "old"
        paid_subscription = subscriber[1]
    else:
        newUser = False
        paid_subscription = subscriber.paid_subscription
    await msg.reply("Меню:", reply_markup=genMainKeyboard(newUser, paid_subscription).as_markup())


async def mainMenu(callback: CallbackQuery, state: FSMContext, bot: Bot, subscriber: UserDB | tuple | bool):
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
        dateNow = datetime.datetime.now()
        locationUser = subscriber.location
        weather = getWeather(locationUser, -1)
        if subscriber.paid_subscription:
            weather += f"\n{getCertainWeather(locationUser, date=[dateNow.day + 1, dateNow.month])}"
        await bot.send_message(
            chat_id=user_id,
            text=weather
        )
    if callback.data == "buySubscription":
        prices = [LabeledPrice(**configPrice)]
        for discount_name in subscriber.discounts:
            discount = dbDiscounts.getDiscount(name=discount_name)
            amount = discount.amount
            label = discount.label
            prices.append(LabeledPrice(amount=(-configPrice["amount"] / 100 * amount),
                                       label=f"Скидка {amount} {label}%"))
        await bot.send_invoice(chat_id=user_id, prices=prices, **configDetails)
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


async def subscribeStep3(msg: Message, state: FSMContext, bot: Bot, time: str, subscriber: UserDB | tuple | bool):
    data = await state.get_data()
    location = data["location"]
    oldUser = False
    if isinstance(subscriber, list):
        oldUser = True
    dbSubscribers.addUser(msg.from_user.id, location, msg.from_user.username, time, subscriber[1] if oldUser else None)
    if not dbScheduler.timeExist(time):
        await scheduler.addTime(time, bot)
    await msg.reply(f"""Вы подписались на ежедневный прогноз погоды!
    Адрес: {location}
    Расписание: Каждый день в {time}
    Платная подписка: {f'от {subscriber[1]}' if oldUser else 'Нет'}""")
    if oldUser:
        dbOldSubscribers.delUser(subscriber[0])
        return await state.clear()
    print(data)
    print(data.get("invited_from"))
    if data.get("invited_from"):
        dbSubscribers.giveDiscount(msg.from_user.id, "invited")
        discount_invited = dbDiscounts.getDiscount(name="invited")
        await msg.reply(f"Вам была выдана скидка в размере {discount_invited.amount}% {discount_invited.label}")
        invited_from_id = decode_payload(data["invited_from"])
        invited_from_user = dbSubscribers.getUser(user_id=invited_from_id)
        discount_inviting_1 = dbDiscounts.getDiscount(name="inviting_1")
        if "inviting_1" not in invited_from_user.discounts:
            dbSubscribers.giveDiscount(invited_from_id, "inviting_1")
            await msg.reply(f"Вам была выдана скидка в размере {discount_inviting_1.amount}% {discount_inviting_1.label}")
        else:
            if len(dbSubscribers.getUsers(invited_from=invited_from_id)) == 5:
                dbSubscribers.removeDiscount(invited_from_id, "inviting_1")
                dbSubscribers.giveDiscount(invited_from_id, "inviting_5")
                discount_inviting_5 = dbDiscounts.getDiscount("inviting_5")
                await msg.reply(f"Вам была выдана скидка в размере {discount_inviting_5.amount}% "
                                f"{discount_inviting_5.label}")
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
    oldTime = dbSubscribers.getUser(user_id=msg.from_user.id).notify_time
    print(dbScheduler.timeExist(time))
    if not dbScheduler.timeExist(time):
        print("awdawd")
        await scheduler.addTime(time, bot)
        dbScheduler.addTime(time)
    subscriber.updateUser(notify_time=time)
    dbScheduler.decreaseCount(oldTime)
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
    dbSubscribers.updateUser(msg.from_user.id, paid_subscription=datetime.datetime.today().strftime('%Y-%m-%d'))
    await msg.answer(f"Платеж на сумму {msg.successful_payment.total_amount // 100}"
                     f"{msg.successful_payment.currency} прошел успешно!!!"
                     f'\nПодписка "Детальный прогноз(1 месяц)" подключена!')


async def start(msg: types.Message, state: FSMContext):
    if " " in msg.text:
        invited_from = msg.text.split(" ")[-1]
        print(invited_from)
        await state.update_data({"invited_from": invited_from})
    await msg.reply(
        text="Укажите ваш населённый пункт(полное название или гео-метка)"
    )
    return await state.set_state(ClientStates.setLoc)
