from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.inline import settings_kb
from bot.keyboards.callbacks import MenuCB, SettingsCB
from db.queries.settings import get_all_settings, toggle_setting

router = Router()


async def _build_settings(callback_or_message):
    current = await get_all_settings()
    text = "\u2699\ufe0f <b>\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u0439</b>\n\n\u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u043d\u0430 \u043a\u043d\u043e\u043f\u043a\u0443, \u0447\u0442\u043e\u0431\u044b \u0432\u043a\u043b\u044e\u0447\u0438\u0442\u044c/\u0432\u044b\u043a\u043b\u044e\u0447\u0438\u0442\u044c:"
    kb = settings_kb(current)
    return text, kb


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    text, kb = await _build_settings(message)
    await message.answer(text, reply_markup=kb)


@router.callback_query(MenuCB.filter(F.action == "settings"))
async def cb_settings_menu(callback: CallbackQuery):
    text, kb = await _build_settings(callback)
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(SettingsCB.filter())
async def cb_toggle_setting(callback: CallbackQuery, callback_data: SettingsCB):
    new_val = await toggle_setting(callback_data.key)
    state = "\u0432\u043a\u043b\u044e\u0447\u0435\u043d\u043e" if new_val else "\u0432\u044b\u043a\u043b\u044e\u0447\u0435\u043d\u043e"
    await callback.answer(f"\u0423\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u0435 {state}", show_alert=False)

    current = await get_all_settings()
    text = "\u2699\ufe0f <b>\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u0439</b>\n\n\u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u043d\u0430 \u043a\u043d\u043e\u043f\u043a\u0443, \u0447\u0442\u043e\u0431\u044b \u0432\u043a\u043b\u044e\u0447\u0438\u0442\u044c/\u0432\u044b\u043a\u043b\u044e\u0447\u0438\u0442\u044c:"
    await callback.message.edit_reply_markup(reply_markup=settings_kb(current))
