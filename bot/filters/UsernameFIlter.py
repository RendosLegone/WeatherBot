from typing import Union, Dict, Any
from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot.misc.util import get_user


class HasUsernamesFilter(BaseFilter):
    """
    Этот фильтр проверяет есть ли в сообщении @usernames
    """
    key = "has_username"

    def __init__(self):
        super().__init__()

    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        """
        :returns: Список с данными о каждом упомянутом пользователе или False
        """
        entities = message.entities or []
        found_usernames = [
            item.extract_from(message.text) for item in entities
            if item.type == "mention"
        ]
        if len(found_usernames) > 0:
            users = []
            for username in found_usernames:
                user = await get_user(username)
                users.append(user)
            return {"users": users}
        return False
