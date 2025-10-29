from aiogram.filters.callback_data import CallbackData


class MenuCB(CallbackData, prefix="menu"):
    action: str


class DealCB(CallbackData, prefix="deal"):
    id: str
    action: str = "view"


class DealListCB(CallbackData, prefix="dlist"):
    page: int = 0
    status: str = "all"


class SettingsCB(CallbackData, prefix="sett"):
    key: str
    action: str = "toggle"


class BalanceCB(CallbackData, prefix="bal"):
    action: str = "current"


class StatsCB(CallbackData, prefix="stat"):
    period: str = "today"
