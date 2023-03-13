from aiogram import Router
from aiogram.filters import Command, StateFilter, CommandObject
from bot.filters import ContentTypeFilter, PreCheckoutQueryFilter, HasTimeFilter, SubscriberFilter
from .client import subscribeStep1, subscribeStep2, subscribeStep3, mainMenu, menuHandler, editTime, editLocation, \
    successful_payment, process_pre_checkout_query
from bot.states import ClientStates


def reg_user_handlers(router: Router):
    router.callback_query.register(mainMenu, SubscriberFilter())
    router.message.register(menuHandler, Command("menu"))
    router.message.register(subscribeStep1, Command("subscribe"))
    router.message.register(subscribeStep2, StateFilter(ClientStates.setLoc))
    router.message.register(subscribeStep3, StateFilter(ClientStates.setTimer), HasTimeFilter(), SubscriberFilter())
    router.message.register(editTime, StateFilter(ClientStates.editTimer), SubscriberFilter())
    router.message.register(editLocation, StateFilter(ClientStates.editLocation))
    router.message.register(successful_payment, ContentTypeFilter(["successful_payment"]))
    router.pre_checkout_query.register(process_pre_checkout_query, PreCheckoutQueryFilter())
