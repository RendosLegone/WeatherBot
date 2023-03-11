from aiogram import Router

from bot.handlers.user import reg_user_handlers
from bot.handlers.admin import reg_admin_handlers
from bot.handlers.others import reg_other_handlers

clientRouter = Router()
adminRouter = Router()
otherRouter = Router()


def reg_all_handlers():
    reg_user_handlers(clientRouter)
    reg_admin_handlers(adminRouter)
    reg_other_handlers(otherRouter)
