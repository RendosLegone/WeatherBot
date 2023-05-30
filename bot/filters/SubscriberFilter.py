from aiogram.filters import Filter
from aiogram.types import Message
from bot.database import UserDB, dbSubscribers, dbOldSubscribers


class SubscriberFilter(Filter):
    def __init__(self):
        super().__init__()

    async def __call__(self, msg: Message) -> dict[str, UserDB] | dict[str, list] | dict[str, None]:
        if not dbSubscribers.getUser(user_id=msg.from_user.id):
            if not dbOldSubscribers.getUser(user_id=msg.from_user.id):
                return {"subscriber": None}
            return {"subscriber": dbOldSubscribers.getUser(user_id=msg.from_user.id)[0]}
        return {"subscriber": dbSubscribers.getUser(user_id=msg.from_user.id)}
