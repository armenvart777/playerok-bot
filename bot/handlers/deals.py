from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.inline import deals_list_kb, deal_detail_kb, back_to_menu_kb
from bot.keyboards.callbacks import MenuCB, DealCB, DealListCB
from db.queries.deals import get_recent_deals, get_deal_by_id
from bot.notifications.templates import STATUS_LABELS
from utils.formatting import format_price, format_dt

router = Router()


async def _build_deals_text(deals, page: int = 0) -> tuple[str, any]:
    if not deals:
        return "\U0001f4e6 <b>\u0421\u0434\u0435\u043b\u043a\u0438</b>\n\n\u041f\u043e\u043a\u0430 \u043d\u0435\u0442 \u0441\u0434\u0435\u043b\u043e\u043a.", back_to_menu_kb()

    text = f"\U0001f4e6 <b>\u0421\u0434\u0435\u043b\u043a\u0438</b> ({len(deals)} \u0432\u0441\u0435\u0433\u043e)\n\n\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0441\u0434\u0435\u043b\u043a\u0443 \u0434\u043b\u044f \u043f\u043e\u0434\u0440\u043e\u0431\u043d\u043e\u0441\u0442\u0435\u0439:"
    kb = deals_list_kb(deals, page)
    return text, kb


@router.message(Command("deals"))
async def cmd_deals(message: Message):
    deals = await get_recent_deals(limit=50)
    text, kb = await _build_deals_text(deals)
    await message.answer(text, reply_markup=kb)


@router.callback_query(MenuCB.filter(F.action == "deals"))
async def cb_deals(callback: CallbackQuery):
    deals = await get_recent_deals(limit=50)
    text, kb = await _build_deals_text(deals)
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(DealListCB.filter())
async def cb_deal_page(callback: CallbackQuery, callback_data: DealListCB):
    deals = await get_recent_deals(limit=50)
    text, kb = await _build_deals_text(deals, page=callback_data.page)
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(DealCB.filter())
async def cb_deal_detail(callback: CallbackQuery, callback_data: DealCB):
    deal = await get_deal_by_id(callback_data.id)
    if not deal:
        await callback.answer("\u0421\u0434\u0435\u043b\u043a\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430", show_alert=True)
        return

    status_label = STATUS_LABELS.get(deal.status, deal.status)
    text = f"""
\U0001f4e6 <b>\u0421\u0434\u0435\u043b\u043a\u0430</b>

\U0001f194 ID: <code>{deal.id}</code>
\U0001f3ae \u0422\u043e\u0432\u0430\u0440: <b>{deal.item_name}</b>
\U0001f464 \u041f\u043e\u043a\u0443\u043f\u0430\u0442\u0435\u043b\u044c: @{deal.buyer_username or 'N/A'}
\U0001f4b5 \u0421\u0443\u043c\u043c\u0430: <b>{format_price(deal.amount)}</b>
\U0001f4cb \u0421\u0442\u0430\u0442\u0443\u0441: {status_label}
\U0001f552 \u0421\u043e\u0437\u0434\u0430\u043d\u043e: {format_dt(deal.created_at)}
\U0001f504 \u041e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u043e: {format_dt(deal.updated_at)}
""".strip()

    await callback.message.edit_text(text, reply_markup=deal_detail_kb(deal.id))
    await callback.answer()
