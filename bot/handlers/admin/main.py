from aiogram import Router
from aiogram.filters import Command
from .admin import testHandler


def reg_admin_handlers(router: Router):
    router.message.register(testHandler, Command("start"))
