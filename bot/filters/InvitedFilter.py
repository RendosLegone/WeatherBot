from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload
from bot.database import dbSubscribers, DiscountDB, dbDiscounts


class InvitedFilter(Filter):
    def __init__(self):
        super().__init__()

    async def __call__(self, msg: Message, state: FSMContext) -> dict[str, dict | None | str]:
        data = await state.get_data()
        if data.get("invited_from"):
            discounts_return = {}
            invited_from_id = int(decode_payload(data["invited_from"]))
            user_id = msg.from_user.id
            if user_id == invited_from_id:
                return {"discounts": "abuse"}
            discount = dbDiscounts.getDiscount(name="invited")
            discounts_return["invited"] = discount
            if "inviting_1" in dbSubscribers.getUser(user_id=invited_from_id).discounts:
                if len(dbSubscribers.getUsers(invited_from=invited_from_id)) == 5:
                    discount = dbDiscounts.getDiscount(name="inviting_5")
                    discounts_return["invited_from"] = discount
            else:
                discount = dbDiscounts.getDiscount(name="inviting_1")
                discounts_return["invited_from"] = discount
            discounts_return["invited_from_id"] = invited_from_id
            return {"discounts": discounts_return}
        return {"discounts": None}
