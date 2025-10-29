from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.inline import stats_period_kb, back_to_menu_kb
from bot.keyboards.callbacks import MenuCB, StatsCB
from db.queries.stats import get_today_stats, get_week_stats, get_month_stats, get_all_time_stats
from db.queries.deals import get_top_items
from utils.formatting import format_price, truncate

router = Router()

PERIOD_LABELS = {
    "today": "\U0001f4c5 \u0421\u0435\u0433\u043e\u0434\u043d\u044f",
    "week": "\U0001f4c6 \u041d\u0435\u0434\u0435\u043b\u044f",
    "month": "\U0001f5d3 \u041c\u0435\u0441\u044f\u0446",
    "all": "\U0001f4cb \u0412\u0441\u0451 \u0432\u0440\u0435\u043c\u044f",
}


async def _build_stats_text(period: str = "today") -> str:
    if period == "today":
        data = await get_today_stats()
    elif period == "week":
        data = await get_week_stats()
    elif period == "month":
        data = await get_month_stats()
    else:
        data = await get_all_time_stats()

    label = PERIOD_LABELS.get(period, period)

    return f"""
\U0001f4c8 <b>\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430</b> \u2014 {label}

\U0001f4e6 \u0421\u0434\u0435\u043b\u043e\u043a: <b>{data['count']}</b>
\U0001f4b0 \u0412\u044b\u0440\u0443\u0447\u043a\u0430: <b>{format_price(data['revenue'])}</b>
\U0001f4ca \u0421\u0440\u0435\u0434\u043d\u0438\u0439 \u0447\u0435\u043a: <b>{format_price(data['avg_deal'])}</b>
""".strip()


async def _build_top_items_text() -> str:
    items = await get_top_items(limit=10)
    if not items:
        return "\U0001f3c6 <b>\u0422\u043e\u043f \u0442\u043e\u0432\u0430\u0440\u043e\u0432</b>\n\n\u041d\u0435\u0442 \u0434\u0430\u043d\u043d\u044b\u0445 \u043e \u043f\u0440\u043e\u0434\u0430\u0436\u0430\u0445"

    lines = ["\U0001f3c6 <b>\u0422\u043e\u043f \u0442\u043e\u0432\u0430\u0440\u043e\u0432 \u043f\u043e \u043f\u0440\u043e\u0434\u0430\u0436\u0430\u043c</b>\n"]
    medals = ["\U0001f947", "\U0001f948", "\U0001f949"]
    for i, item in enumerate(items):
        icon = medals[i] if i < 3 else f"{i + 1}."
        name = truncate(item["item_name"], 35)
        count = item["count"]
        total = format_price(item["total"])
        lines.append(f"{icon} <b>{name}</b>\n   {count} \u043f\u0440\u043e\u0434\u0430\u0436 \u2014 {total}\n")

    return "\n".join(lines)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    text = await _build_stats_text("today")
    await message.answer(text, reply_markup=stats_period_kb())


@router.callback_query(MenuCB.filter(F.action == "stats"))
async def cb_stats_menu(callback: CallbackQuery):
    text = await _build_stats_text("today")
    await callback.message.edit_text(text, reply_markup=stats_period_kb())
    await callback.answer()


@router.callback_query(StatsCB.filter(F.period == "top"))
async def cb_top_items(callback: CallbackQuery):
    text = await _build_top_items_text()
    await callback.message.edit_text(text, reply_markup=stats_period_kb())
    await callback.answer()


@router.callback_query(StatsCB.filter())
async def cb_stats_period(callback: CallbackQuery, callback_data: StatsCB):
    text = await _build_stats_text(callback_data.period)
    await callback.message.edit_text(text, reply_markup=stats_period_kb())
    await callback.answer()
