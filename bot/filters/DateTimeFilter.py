from datetime import timedelta
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

    async def __call__(self, message: Message, command: CommandObject) -> bool | Dict[str, Any]:
        timeData = None
        timeFormat = {"morning": "утра", "day": "дня", "evening": "вечера", "night": "ночи"}
        if command.args[0].find(":") != -1:
            time = command.args[0].split(":")
            hours = int(time[0])
            minutes = int(time[1])
            timeData = timedelta(hours=hours, minutes=minutes)
        else:
            time = command.args[0]
            for i in timeFormat:
                if timeFormat[i] in time:
                    if timeFormat[i] == "дня" or timeFormat[i] == "вечера":
                        timeData = timedelta(hours=int(time.split(f"{timeFormat[i]}")[0]) + 12)
        return {"time": timeData}