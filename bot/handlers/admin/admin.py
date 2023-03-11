from aiogram.types import Message


async def testHandler(msg: Message):
    await msg.reply("Hello!")
