import datetime

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import ClientStates
from bot.misc.util import getLoc
from bot.misc.fconnect import bot
from bot.misc.weather import getCertainWeather
from bot.database import schedulerDB, subscribersDB
from bot.Scheduler import scheduler
from bot.keyboards import genMainKeyboard


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


async def editLocation(msg: Message, state: FSMContext):
    pass

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
