from aiogram.filters import BaseFilter
from aiogram.types import Message


class SuccessfulPaymentFilter(BaseFilter):
    key = "awwd"

    def __init__(self):
        super().__init__()

    async def __call__(self, message: Message) -> bool:
        if message.content_type == "successful_payment":
            return True
        return False
