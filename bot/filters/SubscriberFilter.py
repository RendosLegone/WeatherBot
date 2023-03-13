from aiogram.filters import Filter
from aiogram.types import Message
from bot.database import UserDB, subscribersDB


class SubscriberFilter(Filter):
    def __init__(self):
        super().__init__()

    async def __call__(self, msg: Message) -> dict[str, UserDB | list | False]:
        if not subscribersDB.getUser(msg.from_user.id):
            if not subscribersDB.getOldUser(msg.from_user.id):
                return {"subscriber": False}
            return {"subscriber": subscribersDB.getOldUser(msg.from_user.id)}
        return {"subscriber": subscribersDB.getUser(msg.from_user.id)}
