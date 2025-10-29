from db.engine import get_db


async def is_notification_enabled(key: str) -> bool:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT enabled FROM notification_settings WHERE key = ?", (key,)
    )
    if not rows:
        return True
    return bool(rows[0]["enabled"])


async def toggle_setting(key: str) -> bool:
    db = await get_db()
    current = await is_notification_enabled(key)
    new_val = 0 if current else 1
    await db.execute(
        "UPDATE notification_settings SET enabled = ?, updated_at = datetime('now') WHERE key = ?",
        (new_val, key),
    )
    await db.commit()
    return bool(new_val)


async def get_all_settings() -> dict[str, bool]:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT key, enabled FROM notification_settings")
    return {r["key"]: bool(r["enabled"]) for r in rows}


async def set_setting(key: str, enabled: bool):
    db = await get_db()
    await db.execute(
        "INSERT OR REPLACE INTO notification_settings (key, enabled, updated_at) VALUES (?, ?, datetime('now'))",
        (key, int(enabled)),
    )
    await db.commit()
