from aiogram.filters.state import State, StatesGroup


class ClientStates(StatesGroup):
    setLoc = State()
    setTimer = State()
    editTimer = State()
    editLocation = State()
