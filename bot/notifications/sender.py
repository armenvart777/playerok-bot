import logging
from aiogram import Bot
from config import settings
from db.queries.settings import is_notification_enabled
from bot.notifications.templates import (
    NEW_ORDER, NEW_MESSAGE, NEW_REVIEW, BALANCE_CHANGE, DEAL_STATUS_CHANGE, STATUS_LABELS,
)
from utils.formatting import format_price, format_dt, format_diff, rating_stars, truncate

logger = logging.getLogger(__name__)


class NotificationSender:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def _send(self, text: str, setting_key: str):
        if not await is_notification_enabled(setting_key):
            return
        for admin_id in settings.ADMIN_IDS:
            try:
                await self.bot.send_message(admin_id, text.strip())
            except Exception as e:
                logger.error(f"Failed to notify {admin_id}: {e}")

    async def notify_new_order(self, deal: dict):
        item = deal.get("item") or {}
        user = deal.get("user") or {}
        transaction = deal.get("transaction") or {}
        item_name = item.get("name", "Unknown")
        buyer = user.get("username", "unknown")
        amount = transaction.get("value") or item.get("price", 0)
        text = NEW_ORDER.format(
            item_name=item_name,
            buyer=buyer,
            amount=amount,
            deal_id=deal.get("id", ""),
            time=format_dt(deal.get("createdAt", "")),
        )
        await self._send(text, "notify_new_order")

    async def notify_new_message(self, chat: dict, msg: dict):
        msg_user = msg.get("user") or {}
        sender = msg_user.get("username", "unknown")
        msg_text = truncate(msg.get("text") or "[media]", 200)
        text = NEW_MESSAGE.format(sender=sender, text=msg_text)
        await self._send(text, "notify_new_message")

    async def notify_new_review(self, deal: dict, review: dict):
        item = deal.get("item") or {}
        creator = review.get("creator") or {}
        item_name = item.get("name", "Unknown")
        author = creator.get("username", "unknown")
        text = NEW_REVIEW.format(
            rating=rating_stars(review.get("rating", 0)),
            author=author,
            item_name=item_name,
            text=truncate(review.get("text") or "No text", 200),
        )
        await self._send(text, "notify_new_review")

    async def notify_balance_change(self, old_balance: float, new_balance: float,
                                    diff: float, available: float):
        diff_icon = "\U0001f4c8" if diff >= 0 else "\U0001f4c9"
        text = BALANCE_CHANGE.format(
            old_balance=format_price(old_balance),
            new_balance=format_price(new_balance),
            diff_icon=diff_icon,
            diff=format_diff(diff),
            available=format_price(available),
        )
        await self._send(text, "notify_balance_change")

    async def notify_deal_status_change(self, deal: dict, old_status: str, new_status: str):
        item = deal.get("item") or {}
        item_name = item.get("name", "Unknown")
        old_label = STATUS_LABELS.get(old_status, old_status)
        new_label = STATUS_LABELS.get(new_status, new_status)
        text = DEAL_STATUS_CHANGE.format(
            deal_id=deal.get("id", ""),
            item_name=item_name,
            old_status=old_label,
            new_status=new_label,
        )
        await self._send(text, "notify_deal_status")
