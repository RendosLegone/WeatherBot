from aiogram import Router
from aiogram.filters import Command, StateFilter, CommandObject
from bot.filters import ContentTypeFilter, PreCheckoutQueryFilter, HasTimeFilter, SubscriberFilter, InvitedFilter
from .client import subscribeStep1, subscribeStep2, subscribeStep3, mainMenu, menuHandler, editTime, editLocation, \
    successful_payment, process_pre_checkout_query, start, subscriptions, usePromo
from bot.states import ClientStates


def reg_user_handlers(router: Router):
    router.callback_query.register(mainMenu, SubscriberFilter())
    router.callback_query.register(subscriptions, SubscriberFilter())
    router.message.register(menuHandler, Command("menu"), SubscriberFilter())
    router.message.register(subscribeStep1, Command("subscribe"))
    router.message.register(subscribeStep2, StateFilter(ClientStates.setLoc))
    router.message.register(subscribeStep3, StateFilter(ClientStates.setTimer),
                            HasTimeFilter(), SubscriberFilter(), InvitedFilter())
    router.message.register(editTime, StateFilter(ClientStates.editTimer), HasTimeFilter(),  SubscriberFilter())
    router.message.register(editLocation, StateFilter(ClientStates.editLocation), SubscriberFilter())
    router.message.register(successful_payment, ContentTypeFilter(["successful_payment"]))
    router.pre_checkout_query.register(process_pre_checkout_query, PreCheckoutQueryFilter())
    router.message.register(start, Command("start"), SubscriberFilter())
    router.message.register(usePromo, StateFilter(ClientStates.usePromo), SubscriberFilter())
