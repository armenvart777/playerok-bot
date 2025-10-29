from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.inline import back_to_menu_kb
from bot.keyboards.callbacks import MenuCB
from playerok.client import PlayerokClient
from db.queries.deals import get_deals_count, get_deals_revenue
from db.queries.balance import get_latest_balance
from utils.formatting import format_price

router = Router()

_client: PlayerokClient | None = None


def set_client(client: PlayerokClient):
    global _client
    _client = client


async def _build_status_text() -> str:
    balance_data = None
    username = "N/A"
    if _client and _client.is_connected:
        try:
            balance_data = await _client.get_balance()
            username = _client.username or "N/A"
        except Exception:
            pass

    if not balance_data:
        snap = await get_latest_balance()
        if snap:
            balance_data = {"value": snap.balance, "available": snap.available, "frozen": snap.frozen}

    total_deals = await get_deals_count()
    total_revenue = await get_deals_revenue()

    balance_val = balance_data["value"] if balance_data else 0
    available_val = balance_data["available"] if balance_data else 0
    frozen_val = balance_data["frozen"] if balance_data else 0

    return f"""
\U0001f4ca <b>\u0422\u0435\u043a\u0443\u0449\u0438\u0439 \u0441\u0442\u0430\u0442\u0443\u0441</b>

\U0001f464 \u0410\u043a\u043a\u0430\u0443\u043d\u0442: <b>{username}</b>
\U0001f7e2 \u0421\u0442\u0430\u0442\u0443\u0441: <b>{"Online" if _client and _client.is_connected else "Offline"}</b>

\U0001f4b0 <b>\u0411\u0430\u043b\u0430\u043d\u0441:</b>
   \u0412\u0441\u0435\u0433\u043e: {format_price(balance_val)}
   \u0414\u043e\u0441\u0442\u0443\u043f\u043d\u043e: {format_price(available_val)}
   \u0417\u0430\u043c\u043e\u0440\u043e\u0436\u0435\u043d\u043e: {format_price(frozen_val)}

\U0001f4e6 <b>\u0421\u0434\u0435\u043b\u043a\u0438:</b>
   \u0412\u0441\u0435\u0433\u043e: {total_deals}
   \u041e\u0431\u043e\u0440\u043e\u0442: {format_price(total_revenue)}
""".strip()


@router.message(Command("status"))
async def cmd_status(message: Message):
    text = await _build_status_text()
    await message.answer(text, reply_markup=back_to_menu_kb())


@router.callback_query(MenuCB.filter(F.action == "status"))
async def cb_status(callback: CallbackQuery):
    text = await _build_status_text()
    await callback.message.edit_text(text, reply_markup=back_to_menu_kb())
    await callback.answer()
