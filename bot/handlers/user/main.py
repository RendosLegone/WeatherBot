from aiogram import Router
from aiogram.filters import Command, StateFilter, CommandObject
from bot.filters import ContentTypeFilter, PreCheckoutQueryFilter, HasTimeFilter, SubscriberFilter, MenuFilter
from .client import subscribeStep1, subscribeStep2, subscribeStep3, main_menu, menuHandler, editTime, editLocation, \
    successful_payment, process_pre_checkout_query, start, subscriptions_menu, usePromo, profile_menu
from bot.states import ClientStates
from bot.keyboards import profileButtons, mainButtons, subscriptionsButtons


def reg_user_handlers(router: Router):
    router.pre_checkout_query.register(process_pre_checkout_query, PreCheckoutQueryFilter())
    router.callback_query.register(main_menu, SubscriberFilter(),
                                   MenuFilter(buttons=[button.callback_data for button in mainButtons]))
    router.callback_query.register(subscriptions_menu, SubscriberFilter(),
                                   MenuFilter(buttons=[button.callback_data for button in subscriptionsButtons]))
    router.callback_query.register(profile_menu,
                                   MenuFilter(buttons=[button.callback_data for button in profileButtons]))
    router.message.register(menuHandler, Command("menu"), SubscriberFilter())
    router.message.register(subscribeStep1, Command("subscribe"))
    router.message.register(subscribeStep2, StateFilter(ClientStates.setLoc))
    router.message.register(subscribeStep3, StateFilter(ClientStates.setTimer),  HasTimeFilter(), SubscriberFilter())
    router.message.register(editTime, StateFilter(ClientStates.editTimer), HasTimeFilter(), SubscriberFilter())
    router.message.register(editLocation, StateFilter(ClientStates.editLocation), SubscriberFilter())
    router.message.register(successful_payment, ContentTypeFilter(["successful_payment"]))
    router.message.register(start, Command("start"), SubscriberFilter())
    router.message.register(usePromo, StateFilter(ClientStates.usePromo), SubscriberFilter())
