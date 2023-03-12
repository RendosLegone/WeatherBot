from aiogram.filters import BaseFilter, Filter
from aiogram.types import PreCheckoutQuery


class PreCheckoutQueryFilter(Filter):
    def __init__(self):
        super().__init__()

    async def __call__(self, query: PreCheckoutQuery) -> bool:
        return True