import asyncio
import datetime

import aioschedule
from bot.misc.weather import getWeather, getCertainWeather
from bot.database import schedulerDB, subscribersDB


class Scheduler:
    async def scheduler(self, bot):
        timeData = schedulerDB.getAllTime()
        for time in timeData:
            aioschedule.every(1).day.at(time[0]).do(self.sendWeather, time=time, bot=bot)
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)

    async def addTime(self, time, bot):
        aioschedule.every(1).day.at(time).do(self.sendWeather, time=[time], bot=bot)

    @staticmethod
    async def sendWeather(time, bot):
        dayNow = int(datetime.date.today().strftime("%d"))
        monthNow = int(datetime.date.today().strftime("%m"))
        yearNow = int(datetime.date.today().strftime("%Y"))
        users = subscribersDB.getTimeUsers(time[0])
        for user in users:
            await bot.send_message(chat_id=user[0], text=f"""Добрый день, {user[2]}, вот прогноз на сегодня:
{getWeather(user[1])}""")
            if str(user[4]) != "0":
                if str(user[4].split("-")[0]) == str(yearNow):
                    if monthNow - int(user[4].split("-")[1]) == 1:
                        if int(user[4].split("-")[2]) > dayNow:
                            return await bot.send_message(chat_id=user[0], text=f"""Детальный прогноз(подписка):
                            {getCertainWeather(user[1], [dayNow, monthNow])}""")
                    elif monthNow - int(user[4].split("-")[1]) == 0:
                        return await bot.send_message(chat_id=user[0], text=f"""Детальный прогноз(подписка):
                        {getCertainWeather(user[1], [dayNow, monthNow])}""")
            subscribersDB.updateUser(user[0], paid_subscription="0")


scheduler = Scheduler()
