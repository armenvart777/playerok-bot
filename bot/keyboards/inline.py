from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.callbacks import MenuCB, DealListCB, SettingsCB, StatsCB, BalanceCB, DealCB


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="\U0001f4ca \u0421\u0442\u0430\u0442\u0443\u0441",
                callback_data=MenuCB(action="status").pack(),
            ),
            InlineKeyboardButton(
                text="\U0001f4e6 \u0421\u0434\u0435\u043b\u043a\u0438",
                callback_data=MenuCB(action="deals").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="\U0001f4b0 \u0411\u0430\u043b\u0430\u043d\u0441",
                callback_data=MenuCB(action="balance").pack(),
            ),
            InlineKeyboardButton(
                text="\U0001f4c8 \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430",
                callback_data=MenuCB(action="stats").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="\U0001f4ac \u0421\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f",
                callback_data=MenuCB(action="messages").pack(),
            ),
            InlineKeyboardButton(
                text="\u2699\ufe0f \u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438",
                callback_data=MenuCB(action="settings").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="\U0001f4de \u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430",
                url="https://t.me/supSk1razze_bot",
            ),
            InlineKeyboardButton(
                text="\u2b50 \u041e\u0442\u0437\u044b\u0432\u044b",
                url="https://t.me/sk1razzeotzovy",
            ),
        ],
    ])


def deals_list_kb(deals: list, page: int = 0, page_size: int = 5) -> InlineKeyboardMarkup:
    buttons = []
    start = page * page_size
    end = start + page_size
    page_deals = deals[start:end]

    for deal in page_deals:
        status_icon = {
            "PAID": "\U0001f7e2",
            "SENT": "\U0001f4e8",
            "CONFIRMED": "\u2705",
            "CONFIRMED_AUTOMATICALLY": "\u2705",
            "ROLLED_BACK": "\u274c",
            "PENDING": "\u23f3",
        }.get(deal.status, "\u2753")
        buttons.append([InlineKeyboardButton(
            text=f"{status_icon} {deal.item_name[:30]} | {deal.amount} RUB",
            callback_data=DealCB(id=deal.id).pack(),
        )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(
            text="\u2b05 \u041d\u0430\u0437\u0430\u0434",
            callback_data=DealListCB(page=page - 1).pack(),
        ))
    total_pages = (len(deals) + page_size - 1) // page_size
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(
            text="\u0412\u043f\u0435\u0440\u0435\u0434 \u27a1",
            callback_data=DealListCB(page=page + 1).pack(),
        ))
    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton(
        text="\u2b05 \u041c\u0435\u043d\u044e",
        callback_data=MenuCB(action="menu").pack(),
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def deal_detail_kb(deal_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="\u2b05 \u041a \u0441\u043f\u0438\u0441\u043a\u0443",
            callback_data=MenuCB(action="deals").pack(),
        )],
    ])


def stats_period_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="\U0001f4c5 \u0421\u0435\u0433\u043e\u0434\u043d\u044f",
                callback_data=StatsCB(period="today").pack(),
            ),
            InlineKeyboardButton(
                text="\U0001f4c6 \u041d\u0435\u0434\u0435\u043b\u044f",
                callback_data=StatsCB(period="week").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="\U0001f5d3 \u041c\u0435\u0441\u044f\u0446",
                callback_data=StatsCB(period="month").pack(),
            ),
            InlineKeyboardButton(
                text="\U0001f4cb \u0412\u0441\u0435 \u0432\u0440\u0435\u043c\u044f",
                callback_data=StatsCB(period="all").pack(),
            ),
        ],
        [InlineKeyboardButton(
            text="\U0001f3c6 \u0422\u043e\u043f \u0442\u043e\u0432\u0430\u0440\u043e\u0432",
            callback_data=StatsCB(period="top").pack(),
        )],
        [InlineKeyboardButton(
            text="\u2b05 \u041c\u0435\u043d\u044e",
            callback_data=MenuCB(action="menu").pack(),
        )],
    ])


def settings_kb(current: dict[str, bool]) -> InlineKeyboardMarkup:
    labels = {
        "notify_new_order": "\U0001f4e6 \u041d\u043e\u0432\u044b\u0435 \u0437\u0430\u043a\u0430\u0437\u044b",
        "notify_new_message": "\U0001f4ac \u041d\u043e\u0432\u044b\u0435 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f",
        "notify_new_review": "\u2b50 \u041d\u043e\u0432\u044b\u0435 \u043e\u0442\u0437\u044b\u0432\u044b",
        "notify_balance_change": "\U0001f4b0 \u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0431\u0430\u043b\u0430\u043d\u0441\u0430",
        "notify_deal_status": "\U0001f504 \u0421\u0442\u0430\u0442\u0443\u0441\u044b \u0441\u0434\u0435\u043b\u043e\u043a",
    }

    buttons = []
    for key, label in labels.items():
        enabled = current.get(key, True)
        icon = "\u2705" if enabled else "\u274c"
        buttons.append([InlineKeyboardButton(
            text=f"{icon} {label}",
            callback_data=SettingsCB(key=key).pack(),
        )])

    buttons.append([InlineKeyboardButton(
        text="\u2b05 \u041c\u0435\u043d\u044e",
        callback_data=MenuCB(action="menu").pack(),
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def balance_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="\U0001f4c3 \u0418\u0441\u0442\u043e\u0440\u0438\u044f",
            callback_data=BalanceCB(action="history").pack(),
        )],
        [InlineKeyboardButton(
            text="\u2b05 \u041c\u0435\u043d\u044e",
            callback_data=MenuCB(action="menu").pack(),
        )],
    ])


def back_to_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="\u2b05 \u041c\u0435\u043d\u044e",
            callback_data=MenuCB(action="menu").pack(),
        )],
    ])
