from typing import Dict, Any
from aiogram.filters import BaseFilter, CommandObject
from aiogram.types import Message


class HasTimeFilter(BaseFilter):
    """
    Этот фильтр проверяет наличие указания времени в сообщении
    и, если находит, возвращает словарь с объектом `timedelta`

    :returns: :class: <Dict["messageDateTime", None]> or :class: <Dict["messageDateTime", <datetime>]>
    """

    def __init__(self):
        super().__init__()

    async def __call__(self, msg: Message) -> str | Dict[str, Any]:
        timeData = None
        timeFormat = {"morning": "утра", "day": "дня", "evening": "вечера", "night": "ночи"}
        if msg.text.find(":") != -1:
            return {"time": msg.text}
        else:
            time = msg.text
            for i in timeFormat:
                if timeFormat[i] in time:
                    if timeFormat[i] == "дня" or timeFormat[i] == "вечера":
                        timeData = f"{int(time.split(f'{timeFormat[i]}')[0]) + 12}:00"
        return {"time": timeData}
