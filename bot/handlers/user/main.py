from aiogram import Router
from aiogram.filters import Command, StateFilter
from .client import subscribeStep1, subscribeStep2, subscribeStep3, mainMenu, menuHandler, editTime, editLocation
from bot.states import ClientStates


def reg_user_handlers(router: Router):
    router.callback_query.register(mainMenu)
    router.message.register(menuHandler, Command("menu"))
    router.message.register(subscribeStep1, Command("subscribe"))
    router.message.register(subscribeStep2, StateFilter(ClientStates.setLoc))
    router.message.register(subscribeStep3, StateFilter(ClientStates.setTimer))
    router.message.register(editTime, StateFilter(ClientStates.editTimer))
    router.message.register(editLocation, StateFilter(ClientStates.editLocation))
