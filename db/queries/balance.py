from db.engine import get_db
from db.models import BalanceSnapshot


async def save_balance_snapshot(balance: float, available: float, frozen: float, diff: float):
    db = await get_db()
    await db.execute(
        "INSERT INTO balance_snapshots (balance, available, frozen, diff) VALUES (?, ?, ?, ?)",
        (balance, available, frozen, diff),
    )
    await db.commit()


async def get_latest_balance() -> BalanceSnapshot | None:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM balance_snapshots ORDER BY recorded_at DESC LIMIT 1"
    )
    if not rows:
        return None
    return BalanceSnapshot(**dict(rows[0]))


async def get_balance_history(limit: int = 20) -> list[BalanceSnapshot]:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM balance_snapshots ORDER BY recorded_at DESC LIMIT ?", (limit,)
    )
    return [BalanceSnapshot(**dict(r)) for r in rows]
