import datetime
from aiogram import types, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.fsm.context import FSMContext

from bot.keyboards.mainMenu import genDiscountButton
from bot.states import ClientStates
from bot.misc.util import getLoc
from bot.misc.weather import getCertainWeather, getWeather
from bot.database import schedulerDB, subscribersDB, UserDB
from bot.Scheduler import scheduler
from bot.keyboards import genMainKeyboard
from bot.misc.config import configPrice, configDetails, configDiscounts


async def menuHandler(msg: Message, subscriber: UserDB | tuple | bool):
    if not subscriber:
        newUser = True
        paid_subscription = 0
    elif isinstance(subscriber, tuple):
        newUser = "old"
        paid_subscription = subscriber[1]
    else:
        newUser = False
        paid_subscription = subscriber.paid_subscription
    await msg.reply("Меню:", reply_markup=genMainKeyboard(newUser, paid_subscription).as_markup())


async def mainMenu(callback: CallbackQuery, state: FSMContext, bot: Bot, subscriber: UserDB | tuple | bool):
    user_id = callback.from_user.id
    await bot.delete_message(message_id=callback.message.message_id, chat_id=user_id)
    someData = None
    if len(callback.data.split("_")) > 1:
        someData = callback.data.split("_")[1]

    if callback.data.split("_")[0] == "subscribe":
        if int(someData) == callback.from_user.id:
            return await callback.answer("Приглашать самого себя нельзя!", show_alert=True)
        await bot.send_message(
            chat_id=user_id,
            text="Укажите ваш населённый пункт(полное название или гео-метка)"
        )
        await state.set_state(ClientStates.setLoc)
        await state.update_data(data={"inviting": someData})
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
        if subscriber.discount != 0:
            prices.append(LabeledPrice(amount=(-configPrice["amount"] / 100 * subscriber.discount),
                                       label=f"Скидка {subscriber.discount}%"))
        await bot.send_invoice(chat_id=user_id, prices=prices, **configDetails)
    if callback.data == "resubscribe":
        await bot.send_message(
            chat_id=user_id,
            text="Укажите ваш населённый пункт(полное название или гео-метка)"
        )
        await state.set_state(ClientStates.setLoc)
    if callback.data == "getDiscount":
        if subscriber.discount != 0:
            return await callback.answer("Вы уже приглашали друга!", show_alert=True)
        await bot.send_message(
            chat_id=user_id,
            text="Чтобы получить скидку нужно пригласить друга, просто отправьте ему это сообщение",
            reply_markup=genDiscountButton(user_id).as_markup()
        )


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
    if isinstance(subscriber, tuple):
        oldUser = True
    subscribersDB.addUser(msg.from_user.id, location, msg.from_user.username, time, subscriber[1] if oldUser else 0)
    await scheduler.addTime(time, bot)
    await msg.reply(f"""Вы подписались на ежедневный прогноз погоды!
    Адрес: {location}
    Расписание: Каждый день в {time}
    Платная подписка: {f'от {subscriber[1]}' if oldUser else 'Нет'}""")
    if oldUser:
        subscribersDB.delOldUser(subscriber[0])
        return await state.clear()
    subscriber = subscribersDB.getUser(msg.from_user.id)
    if configDiscounts["global"]:
        subscriber.updateUser(discount=configDiscounts["global"])
    if data["inviting"]:
        subscriber.updateUser(discount=subscriber.discount + configDiscounts["inviting"])
        inviting = subscribersDB.getUser(data["inviting"])
        inviting.updateUser(inviting.discount + configDiscounts["inviting"])
        await msg.reply(f"Вы и ваш друг получаете скидку {configDiscounts['inviting']}% на платную подписку!")
        await bot.send_message(chat_id=data["inviting"],
                               text=f"Вам была присвоена скидка {configDiscounts['inviting']}% за приглашение друга!")
    await msg.reply(f"Оформить платную подписку на детальный прогноз можно в /menu ;)")
    return await state.clear()


async def editLocation(msg: Message, state: FSMContext, subscriber: UserDB | tuple | bool):
    if msg.location:
        location = getLoc(msg.location.latitude, msg.location.longitude)
    else:
        location = msg.text
    subscriber.updateUser(location=location)
    await msg.reply("Ваш адрес изменён!")
    await state.clear()


async def editTime(msg: Message, state: FSMContext, bot: Bot, subscriber: UserDB | tuple | bool):
    oldTime = subscribersDB.getUser(msg.from_user.id).notifyTime
    print(subscriber)
    subscriber.updateUser(notifyTime=msg.text)
    schedulerDB.decreaseCount(oldTime)
    if schedulerDB.timeExist(msg.text) is False:
        await scheduler.addTime(msg.text, bot)
        schedulerDB.addTime(msg.text)
        schedulerDB.increaseCount(msg.text)
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
    subscribersDB.updateUser(msg.from_user.id, paid_subscription=datetime.datetime.today().strftime('%Y-%m-%d'))
    await msg.answer(f"Платеж на сумму {msg.successful_payment.total_amount // 100}"
                     f"{msg.successful_payment.currency} прошел успешно!!!"
                     f'\nПодписка "Детальный прогноз(1 месяц)" подключена!')
