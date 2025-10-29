from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import settings
from bot.middlewares.admin_only import AdminOnlyMiddleware


def create_bot() -> Bot:
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(AdminOnlyMiddleware())
    dp.callback_query.middleware(AdminOnlyMiddleware())

    from bot.handlers import start, status, deals, balance, stats, messages, settings as settings_handler
    dp.include_router(start.router)
    dp.include_router(status.router)
    dp.include_router(deals.router)
    dp.include_router(balance.router)
    dp.include_router(stats.router)
    dp.include_router(messages.router)
    dp.include_router(settings_handler.router)

    return dp
