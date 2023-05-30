from aiogram.filters import Filter
from aiogram.types import CallbackQuery


class MenuFilter(Filter):
    def __init__(self, buttons: list):
        super().__init__()
        self.buttons = buttons

    async def __call__(self, callback: CallbackQuery) -> bool:
        if callback.data.split("__")[0] in self.buttons:
            return True
        return False
