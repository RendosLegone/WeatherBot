from aiogram.filters import BaseFilter
from aiogram.types import Message


class ContentTypeFilter(BaseFilter):
    __slots__ = ("content_types",)

    def __init__(self, content_types):
        super().__init__()
        self.content_types = content_types

    async def __call__(self, message: Message) -> bool:
        if message.content_type in self.content_types:
            return True
        return False