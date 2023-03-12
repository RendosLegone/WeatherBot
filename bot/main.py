from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers.main import clientRouter, adminRouter, otherRouter, reg_all_handlers
import asyncio
from bot.Scheduler import scheduler
from bot.misc.env import TgKeys

bot = Bot(token=TgKeys.TOKEN)


async def on_startup():
    asyncio.create_task(scheduler.scheduler(bot))


async def run_bot():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(clientRouter)
    dp.include_router(adminRouter)
    dp.include_router(otherRouter)
    reg_all_handlers()
    dp.startup.register(on_startup)
    await dp.start_polling(bot, skip_updates=True)
