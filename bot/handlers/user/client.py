import datetime
from aiogram import types
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.fsm.context import FSMContext
from bot.states import ClientStates
from bot.misc.util import getLoc
from bot.misc.fconnect import bot
from bot.misc.weather import getCertainWeather
from bot.database import schedulerDB, subscribersDB
from bot.Scheduler import scheduler
from bot.keyboards import genMainKeyboard
from configparser import ConfigParser
config = ConfigParser()
config.read("F:/Программирование/Python проекты/Bot-Site Project/bot/handlers/user/config.ini",
            encoding="UTF-8")
print(config["ONE_MONTH_SUBSCRIBE_DETAILS"])
configDetails = {}
configPrice = {}
for key in config["ONE_MONTH_SUBSCRIBE_DETAILS"]:
    value = config["ONE_MONTH_SUBSCRIBE_DETAILS"][key]
    if "width" in key or "height" in key or "size" in key:
        value = int(value)
    if "flex" in key:
        value = bool(value)
    configDetails[key] = value
for key in config["ONE_MONTH_SUBSCRIBE_PRICE"]:
    value = config["ONE_MONTH_SUBSCRIBE_PRICE"][key]
    if key == "amount":
        value = int(value)
    configPrice[key] = value
print(configDetails)


async def menuHandler(msg: Message):
    if subscribersDB.getUser(msg.from_user.id) is False:
        newUser = True
    else:
        newUser = False
    await msg.reply("Меню:", reply_markup=genMainKeyboard(newUser).as_markup())


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


async def subscribeStep3(msg: Message, state: FSMContext):
    data = await state.get_data()
    location = data["location"]
    time = msg.text
    subscribersDB.addUser(msg.from_user.id, location, msg.from_user.username, time)
    await scheduler.addTime(time)


async def mainMenu(callback: CallbackQuery, state: FSMContext):
    if callback.data == "subscribe":
        await bot.send_message(
            chat_id=callback.from_user.id,
            text="Укажите ваш населённый пункт(полное название или гео-метка)"
        )
        await state.set_state(ClientStates.setLoc)
    if callback.data == "unsubscribe":
        subscribersDB.delUser(callback.from_user.id)
        await bot.send_message(
            chat_id=callback.from_user.id,
            text="Вы отписались от прогноза погоды"
        )
    if callback.data == "editTime":
        await bot.send_message(
            chat_id=callback.from_user.id,
            text="Во сколько вы хотите получать ежедневную рассылку?"
        )
        await state.set_state(ClientStates.editTimer)
    if callback.data == "editLocation":
        await bot.send_message(
            chat_id=callback.from_user.id,
            text="Укажите ваш населённый пункт(полное название или гео-метка)"
        )
        await state.set_state(ClientStates.editLocation)
    if callback.data == "getWeather":
        dateNow = datetime.datetime.now()
        locationUser = subscribersDB.getUser(callback.from_user.id).location
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=getCertainWeather(locationUser, date=[dateNow.day + 1, dateNow.month])
        )
    if callback.data == "buySubscription":
        await bot.send_invoice(chat_id=callback.from_user.id, prices=[LabeledPrice(**configPrice)], **configDetails)


async def editLocation(msg: Message, state: FSMContext):
    subscribersDB.updateUser(msg.from_user.id, location=msg.text)
    await msg.reply("Ваш адрес изменён!")
    await state.clear()


async def editTime(msg: Message, state: FSMContext):
    oldTime = subscribersDB.getUser(msg.from_user.id).notifyTime
    subscribersDB.updateUser(msg.from_user.id, notifyTime=msg.text)
    schedulerDB.decreaseCount(oldTime)
    if schedulerDB.timeExist(msg.text) is False:
        await scheduler.addTime(msg.text)
        schedulerDB.addTime(msg.text)
        schedulerDB.increaseCount(msg.text)
    await msg.reply("Время рассылки успешно изменено!")
    await state.clear()


async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    print("dwwadw")
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)
    print("dwadwawd")


async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment
    for k, v in payment_info:
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100} "
                           f"{message.successful_payment.currency} прошел успешно!!!")