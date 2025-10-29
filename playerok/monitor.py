import asyncio
import logging
from playerok.client import PlayerokClient
from db.models import Deal, Message, Review
from db.queries.deals import save_deal, get_deal_ids, update_deal_status, get_recent_deals
from db.queries.messages import save_message, get_all_message_ids
from db.queries.balance import save_balance_snapshot, get_latest_balance
from config import settings

logger = logging.getLogger(__name__)


class PlayerokMonitor:
    def __init__(self, client: PlayerokClient, notification_sender):
        self.client = client
        self.sender = notification_sender
        self._running = False
        self._last_balance: float | None = None
        self._known_deal_ids: set[str] = set()
        self._known_message_ids: set[str] = set()
        self._deal_statuses: dict[str, str] = {}

    async def start(self):
        self._running = True
        self._known_deal_ids = await get_deal_ids()
        self._known_message_ids = await get_all_message_ids()

        # Load deal statuses from DB so we can detect changes after restart
        existing_deals = await get_recent_deals(limit=100)
        for d in existing_deals:
            self._deal_statuses[d.id] = d.status

        last_snap = await get_latest_balance()
        if last_snap:
            self._last_balance = last_snap.balance

        logger.info(
            f"Monitor starting: {len(self._known_deal_ids)} known deals, "
            f"{len(self._known_message_ids)} known messages"
        )
        asyncio.create_task(self._poll_deals())
        asyncio.create_task(self._poll_messages())
        asyncio.create_task(self._poll_balance())
        logger.info("Monitor started - polling deals, messages, balance")

    async def stop(self):
        self._running = False
        logger.info("Monitor stopped")

    async def _poll_deals(self):
        while self._running:
            try:
                await self._check_deals()
            except Exception as e:
                logger.error(f"Deal poll error: {e}", exc_info=True)
            await asyncio.sleep(settings.DEALS_POLL_INTERVAL)

    async def _poll_messages(self):
        while self._running:
            try:
                await self._check_messages()
            except Exception as e:
                logger.error(f"Message poll error: {e}", exc_info=True)
            await asyncio.sleep(settings.DEALS_POLL_INTERVAL)

    async def _poll_balance(self):
        while self._running:
            try:
                await self._check_balance()
            except Exception as e:
                logger.error(f"Balance poll error: {e}", exc_info=True)
            await asyncio.sleep(settings.BALANCE_POLL_INTERVAL)

    async def _check_deals(self):
        # Fetch all deals (no direction filter — API enum may differ)
        deals = await self.client.get_deals(count=20)
        if not deals:
            logger.debug("No deals returned from API")
            return

        logger.debug(f"API returned {len(deals)} deals")

        for deal in deals:
            deal_id = deal.get("id", "")
            status_name = deal.get("status", "UNKNOWN")
            direction = deal.get("direction", "")

            if deal_id not in self._known_deal_ids:
                self._known_deal_ids.add(deal_id)
                item = deal.get("item") or {}
                user = deal.get("user") or {}
                transaction = deal.get("transaction") or {}

                amount = transaction.get("value") or item.get("price", 0)
                # Ensure amount is a number
                try:
                    amount = float(amount)
                except (ValueError, TypeError):
                    amount = 0.0

                db_deal = Deal(
                    id=deal_id,
                    item_name=item.get("name", "Unknown"),
                    item_id=item.get("id"),
                    buyer_username=user.get("username"),
                    buyer_id=user.get("id"),
                    amount=amount,
                    status=status_name,
                    direction=direction or "sale",
                    created_at=deal.get("createdAt", ""),
                    updated_at="",
                )
                await save_deal(db_deal)
                self._deal_statuses[deal_id] = status_name

                # Notify about any new deal (not just PAID/PENDING)
                await self.sender.notify_new_order(deal)
                logger.info(f"New deal: {deal_id} - {db_deal.item_name} [{status_name}] ({direction})")

            elif deal_id in self._deal_statuses and self._deal_statuses[deal_id] != status_name:
                old_status = self._deal_statuses[deal_id]
                self._deal_statuses[deal_id] = status_name
                await update_deal_status(deal_id, old_status, status_name)
                await self.sender.notify_deal_status_change(deal, old_status, status_name)
                logger.info(f"Deal {deal_id} status: {old_status} -> {status_name}")
            elif deal_id not in self._deal_statuses:
                # Deal is in DB but statuses not loaded (shouldn't happen now, but safety net)
                self._deal_statuses[deal_id] = status_name

        # Check for reviews (API field is "testimonial") on confirmed deals
        for deal in deals:
            review = deal.get("testimonial") or deal.get("review")
            if review and review.get("id"):
                await self._handle_review(deal, review)

    async def _handle_review(self, deal: dict, review: dict | None = None):
        if review is None:
            review = deal.get("testimonial") or deal.get("review") or {}
        review_id = review.get("id")
        if not review_id:
            return

        from db.engine import get_db
        db = await get_db()
        rows = await db.execute_fetchall("SELECT id FROM reviews WHERE id = ?", (review_id,))
        if rows:
            return

        creator = review.get("creator") or {}
        db_review = Review(
            id=review_id,
            deal_id=deal.get("id", ""),
            rating=review.get("rating", 0),
            text=review.get("text", ""),
            author_username=creator.get("username"),
            status=review.get("status"),
            created_at=review.get("createdAt", ""),
        )
        await db.execute(
            "INSERT OR IGNORE INTO reviews (id, deal_id, rating, text, author_username, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (db_review.id, db_review.deal_id, db_review.rating, db_review.text,
             db_review.author_username, db_review.status, db_review.created_at),
        )
        await db.commit()
        await self.sender.notify_new_review(deal, review)
        logger.info(f"New review: {review_id} for deal {deal.get('id')}")

    async def _check_messages(self):
        chats = await self.client.get_chats(count=10)
        if not chats:
            return

        for chat in chats:
            unread = chat.get("unreadMessagesCounter", 0)
            if unread <= 0:
                continue

            chat_id = chat.get("id", "")
            messages = await self.client.get_chat_messages(chat_id, count=5)
            if not messages:
                continue

            for msg in messages:
                msg_id = msg.get("id", "")
                if msg_id in self._known_message_ids:
                    continue
                if msg.get("isRead"):
                    continue
                # Skip own messages
                msg_user = msg.get("user") or {}
                if self.client._user_id and msg_user.get("id") == self.client._user_id:
                    continue

                self._known_message_ids.add(msg_id)
                db_msg = Message(
                    id=msg_id,
                    chat_id=chat_id,
                    sender_username=msg_user.get("username"),
                    sender_id=msg_user.get("id"),
                    text=msg.get("text"),
                    is_system=False,
                    received_at=msg.get("createdAt", ""),
                )
                await save_message(db_msg)
                await self.sender.notify_new_message(chat, msg)
                logger.info(f"New message from {db_msg.sender_username}: {(db_msg.text or 'N/A')[:50]}")

    async def _check_balance(self):
        balance_data = await self.client.get_balance()
        if "error" in balance_data or balance_data.get("value", 0) == 0 and self._last_balance and self._last_balance > 0:
            # API error or suspicious zero — skip this cycle
            return
        current = balance_data["value"]

        if self._last_balance is not None and current != self._last_balance:
            diff = current - self._last_balance
            await save_balance_snapshot(
                balance=current,
                available=balance_data["available"],
                frozen=balance_data["frozen"],
                diff=diff,
            )
            await self.sender.notify_balance_change(
                old_balance=self._last_balance,
                new_balance=current,
                diff=diff,
                available=balance_data["available"],
            )
            logger.info(f"Balance changed: {self._last_balance} -> {current} (diff: {diff:+})")

        if self._last_balance is None:
            await save_balance_snapshot(
                balance=current,
                available=balance_data["available"],
                frozen=balance_data["frozen"],
                diff=0,
            )

        self._last_balance = current
