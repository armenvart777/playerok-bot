from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.inline import balance_kb, back_to_menu_kb
from bot.keyboards.callbacks import MenuCB, BalanceCB
from playerok.client import PlayerokClient
from db.queries.balance import get_latest_balance, get_balance_history
from utils.formatting import format_price, format_diff, format_dt

router = Router()

_client: PlayerokClient | None = None


def set_client(client: PlayerokClient):
    global _client
    _client = client


async def _build_balance_text() -> str:
    balance_data = None
    if _client and _client.is_connected:
        try:
            balance_data = await _client.get_balance()
        except Exception:
            pass

    if not balance_data:
        snap = await get_latest_balance()
        if snap:
            balance_data = {"value": snap.balance, "available": snap.available, "frozen": snap.frozen, "pending_income": 0}

    if not balance_data:
        return "\U0001f4b0 <b>\u0411\u0430\u043b\u0430\u043d\u0441</b>\n\n\u041d\u0435\u0442 \u0434\u0430\u043d\u043d\u044b\u0445. \u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0438\u0442\u0435 Playerok \u0430\u043a\u043a\u0430\u0443\u043d\u0442."

    return f"""
\U0001f4b0 <b>\u0411\u0430\u043b\u0430\u043d\u0441 Playerok</b>

\U0001f4b3 \u0412\u0441\u0435\u0433\u043e: <b>{format_price(balance_data['value'])}</b>
\u2705 \u0414\u043e\u0441\u0442\u0443\u043f\u043d\u043e: {format_price(balance_data['available'])}
\u2744\ufe0f \u0417\u0430\u043c\u043e\u0440\u043e\u0436\u0435\u043d\u043e: {format_price(balance_data['frozen'])}
\u23f3 \u041e\u0436\u0438\u0434\u0430\u0435\u0442\u0441\u044f: {format_price(balance_data.get('pending_income', 0))}
""".strip()


async def _build_history_text() -> str:
    history = await get_balance_history(limit=10)
    if not history:
        return "\U0001f4b0 <b>\u0418\u0441\u0442\u043e\u0440\u0438\u044f \u0431\u0430\u043b\u0430\u043d\u0441\u0430</b>\n\n\u041f\u043e\u043a\u0430 \u043d\u0435\u0442 \u0437\u0430\u043f\u0438\u0441\u0435\u0439."

    lines = ["\U0001f4b0 <b>\u0418\u0441\u0442\u043e\u0440\u0438\u044f \u0431\u0430\u043b\u0430\u043d\u0441\u0430</b>\n"]
    for snap in history:
        icon = "\U0001f4c8" if snap.diff >= 0 else "\U0001f4c9"
        lines.append(
            f"{icon} {format_dt(snap.recorded_at)}: {format_price(snap.balance)} ({format_diff(snap.diff)})"
        )

    return "\n".join(lines)


@router.message(Command("balance"))
async def cmd_balance(message: Message):
    text = await _build_balance_text()
    await message.answer(text, reply_markup=balance_kb())


@router.callback_query(MenuCB.filter(F.action == "balance"))
async def cb_balance(callback: CallbackQuery):
    text = await _build_balance_text()
    await callback.message.edit_text(text, reply_markup=balance_kb())
    await callback.answer()


@router.callback_query(BalanceCB.filter(F.action == "history"))
async def cb_balance_history(callback: CallbackQuery):
    text = await _build_history_text()
    await callback.message.edit_text(text, reply_markup=back_to_menu_kb())
    await callback.answer()
