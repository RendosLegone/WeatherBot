import asyncio
import aioschedule
from bot.misc.fconnect import bot
from bot.misc.weather import getWeather
from bot.database import schedulerDB, subscribersDB


class Scheduler:
    async def scheduler(self):
        timeData = schedulerDB.getAllTime()
        for time in timeData:
            aioschedule.every(1).day.at(time[0]).do(self.sendWeather, time=time)
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)

    async def addTime(self, time):
        aioschedule.every(1).day.at(time).do(self.sendWeather, time=[time])

    @staticmethod
    async def sendWeather(time):
        users = subscribersDB.getTimeUsers(time[0])
        for user in users:
            await bot.send_message(chat_id=user[0], text=f"""Добрый день, {user[2]}, вот прогноз на сегодня:
{getWeather(user[1])}""")


scheduler = Scheduler()
