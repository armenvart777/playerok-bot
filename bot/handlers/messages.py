from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message as TgMessage, CallbackQuery
from bot.keyboards.inline import back_to_menu_kb
from bot.keyboards.callbacks import MenuCB
from db.queries.messages import get_recent_messages
from utils.formatting import format_dt, truncate

router = Router()


async def _build_messages_text() -> str:
    messages = await get_recent_messages(limit=15)
    if not messages:
        return "\U0001f4ac <b>\u0421\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f</b>\n\n\u041d\u0435\u0442 \u043d\u043e\u0432\u044b\u0445 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0439"

    lines = ["\U0001f4ac <b>\u0421\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f</b> (\u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0435 15)\n"]
    for msg in messages:
        sender = msg.sender_username or "system"
        text = truncate(msg.text or "[media]", 80)
        time = format_dt(msg.received_at)
        lines.append(f"\U0001f464 <b>@{sender}</b> \u2014 {time}\n\U0001f4dd {text}\n")

    return "\n".join(lines)


@router.message(Command("messages"))
async def cmd_messages(message: TgMessage):
    text = await _build_messages_text()
    await message.answer(text, reply_markup=back_to_menu_kb())


@router.callback_query(MenuCB.filter(F.action == "messages"))
async def cb_messages(callback: CallbackQuery):
    text = await _build_messages_text()
    await callback.message.edit_text(text, reply_markup=back_to_menu_kb())
    await callback.answer()
