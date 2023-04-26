import asyncio
import datetime
import aioschedule
from bot.misc.weather import getWeather, getCertainWeather
from bot.database import dbScheduler, dbSubscribers


class Scheduler:
    async def scheduler(self, bot):
        timeData = dbScheduler.getTime()
        if timeData:
            for time in timeData:
                time = time.time.strftime("%H:%M")
                aioschedule.every(1).day.at(time).do(self.sendWeather, time=[time], bot=bot)
            while True:
                await aioschedule.run_pending()
                await asyncio.sleep(1)

    async def addTime(self, time, bot):
        print(time)
        aioschedule.every(1).day.at(time).do(self.sendWeather, time=[time], bot=bot)

    @staticmethod
    async def sendWeather(time, bot):
        dayNow = int(datetime.date.today().day)
        monthNow = int(datetime.date.today().month)
        users = dbSubscribers.getUsers(notify_time=time[0])
        for user in users:
            await bot.send_message(chat_id=user.user_id, text=f"""Добрый день, {user.username}, вот прогноз на сегодня:
            {getWeather(user.location)}""")
            if user.paid_subscription:
                sub_date = datetime.date.today() - user.paid_subscription
                if sub_date.days < 31:
                    return await bot.send_message(chat_id=user.user_id, text=f"""Детальный прогноз(подписка):
                    {getCertainWeather(user.location, [dayNow, monthNow])}""")
                return dbSubscribers.updateUser(user.user_id, paid_subscription=None)


scheduler = Scheduler()
