from abc import ABC

from aiogram import types
from aiogram.filters import Filter, BaseFilter
from aiogram.types import ContentType, Message


# class ContentTypeFilter(Filter):
#     """
#     Check message content type
#     """
#
#     key = 'content_types'
#     required = True
#     default = ContentType.TEXT
#
#     def __init__(self, content_types):
#         if isinstance(content_types, str):
#             content_types = (content_types,)
#         self.content_types = content_types
#
#     async def __call__(self, message):
#         return types.ContentType.ANY in self.content_types or \
#                message.content_type in self.content_types
class SuccessfulPaymentFilter(BaseFilter):
    key = "awwd"

    def __init__(self):
        super().__init__()

    async def __call__(self, message: Message) -> bool:
        if message.content_type == "successful_payment":
            return True
        return False
