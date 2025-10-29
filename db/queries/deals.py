from db.engine import get_db
from db.models import Deal


def _normalize_dt(dt_str: str) -> str:
    """Normalize ISO datetime (2026-02-13T16:05:28.000Z) to SQLite-friendly format."""
    if not dt_str:
        return ""
    dt_str = dt_str.replace("T", " ")
    if dt_str.endswith("Z"):
        dt_str = dt_str[:-1]
    if "." in dt_str:
        dt_str = dt_str.split(".")[0]
    return dt_str


async def save_deal(deal: Deal):
    db = await get_db()
    created = _normalize_dt(deal.created_at)
    await db.execute(
        """INSERT OR REPLACE INTO deals
           (id, item_name, item_id, buyer_username, buyer_id, amount, status, direction, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
        (deal.id, deal.item_name, deal.item_id, deal.buyer_username,
         deal.buyer_id, deal.amount, deal.status, deal.direction, created),
    )
    await db.commit()


async def update_deal_status(deal_id: str, old_status: str | None, new_status: str):
    db = await get_db()
    await db.execute(
        "UPDATE deals SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (new_status, deal_id),
    )
    await db.execute(
        "INSERT INTO deal_status_history (deal_id, old_status, new_status) VALUES (?, ?, ?)",
        (deal_id, old_status, new_status),
    )
    await db.commit()


async def get_deal_by_id(deal_id: str) -> Deal | None:
    db = await get_db()
    row = await db.execute_fetchall(
        "SELECT * FROM deals WHERE id = ?", (deal_id,)
    )
    if not row:
        return None
    r = row[0]
    return Deal(**dict(r))


async def get_recent_deals(limit: int = 20, status: str | None = None) -> list[Deal]:
    db = await get_db()
    if status:
        rows = await db.execute_fetchall(
            "SELECT * FROM deals WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            (status, limit),
        )
    else:
        rows = await db.execute_fetchall(
            "SELECT * FROM deals ORDER BY created_at DESC LIMIT ?", (limit,)
        )
    return [Deal(**dict(r)) for r in rows]


async def get_deal_ids() -> set[str]:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT id FROM deals")
    return {r["id"] for r in rows}


async def get_deals_count() -> int:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT COUNT(*) as cnt FROM deals")
    return rows[0]["cnt"]


async def get_deals_revenue() -> float:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT COALESCE(SUM(amount), 0) as total FROM deals"
    )
    return rows[0]["total"]


async def get_deals_count_by_period(start: str, end: str) -> int:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT COUNT(*) as cnt FROM deals WHERE created_at BETWEEN ? AND ?",
        (start, end),
    )
    return rows[0]["cnt"]


async def get_revenue_by_period(start: str, end: str) -> float:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT COALESCE(SUM(amount), 0) as total FROM deals WHERE created_at BETWEEN ? AND ?",
        (start, end),
    )
    return rows[0]["total"]


async def get_top_items(limit: int = 10) -> list[dict]:
    db = await get_db()
    rows = await db.execute_fetchall(
        """SELECT item_name, COUNT(*) as count, COALESCE(SUM(amount), 0) as total
           FROM deals
           GROUP BY item_name
           ORDER BY count DESC
           LIMIT ?""",
        (limit,),
    )
    return [dict(r) for r in rows]
