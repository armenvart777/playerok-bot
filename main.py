import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from utils.logging_config import setup_logging
from db.engine import close_db
from db.migrations import init_db
from playerok.client import PlayerokClient
from playerok.monitor import PlayerokMonitor
from bot.setup import create_bot, create_dispatcher
from bot.notifications.sender import NotificationSender
from bot.handlers.status import set_client as set_status_client
from bot.handlers.balance import set_client as set_balance_client


async def main():
    ...


if __name__ == "__main__":
    asyncio.run(main())
