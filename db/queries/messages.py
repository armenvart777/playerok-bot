from db.engine import get_db
from db.models import Message


async def save_message(msg: Message):
    db = await get_db()
    await db.execute(
        """INSERT OR IGNORE INTO messages
           (id, chat_id, sender_username, sender_id, text, is_system, received_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (msg.id, msg.chat_id, msg.sender_username, msg.sender_id,
         msg.text, int(msg.is_system), msg.received_at),
    )
    await db.commit()


async def get_message_ids_for_chat(chat_id: str) -> set[str]:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT id FROM messages WHERE chat_id = ?", (chat_id,)
    )
    return {r["id"] for r in rows}


async def get_all_message_ids() -> set[str]:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT id FROM messages")
    return {r["id"] for r in rows}


async def get_recent_messages(limit: int = 20) -> list[Message]:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM messages ORDER BY received_at DESC LIMIT ?", (limit,)
    )
    return [Message(**dict(r)) for r in rows]
