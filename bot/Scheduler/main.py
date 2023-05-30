import asyncio
import datetime
import aioschedule
from bot.misc.weather import getWeather, getCertainWeather
from bot.database import dbScheduler, dbSubscribers, dbSubscriptions, dbReceipts


class Scheduler:
    async def scheduler(self, bot):
        time_data = dbScheduler.getTime()
        if time_data:
            for time in time_data:
                time = time.time.strftime("%H:%M")
                aioschedule.every(1).day.at(time).do(self.sendWeather, time=[time], bot=bot)
            while True:
                await aioschedule.run_pending()
                await asyncio.sleep(1)

    async def addTime(self, time, bot):
        aioschedule.every(1).day.at(time).do(self.sendWeather, time=[time], bot=bot)

    @staticmethod
    async def sendWeather(time, bot):
        date_time = datetime.datetime.now()
        day_now = int(date_time.day)
        month_now = int(date_time.month)
        users = dbSubscribers.getUsers(notify_time=time[0])
        for user in users:
            await bot.send_message(chat_id=user.user_id, text=f"""Добрый день, {user.username}, вот прогноз на сегодня:
            {getWeather(user.location)}""")
            if user.paid_subscription_id:
                receipt = dbReceipts.getReceipt(user_id=user.user_id)
                subscription = dbSubscriptions.getSubscription(name=receipt.subscription_name)
                sub_date = receipt.date_time + subscription.period
                if date_time < sub_date:
                    return await bot.send_message(chat_id=user.user_id, text=f"""Детальный прогноз(подписка):
                    {getCertainWeather(user.location, [day_now, month_now])}""")
                await bot.send_message(chat_id=user.user_id, text=f"Ваша {subscription.label} истекла, "
                                                                  f"продлить подписку можно в /menu ;)")
                return dbSubscribers.updateUser(user.user_id, paid_subscription_id=None)


scheduler = Scheduler()
