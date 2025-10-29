from datetime import datetime, timedelta
from db.engine import get_db


async def get_stats_for_period(start: str, end: str) -> dict:
    db = await get_db()

    count_row = await db.execute_fetchall(
        "SELECT COUNT(*) as cnt FROM deals WHERE created_at BETWEEN ? AND ?",
        (start, end),
    )
    revenue_row = await db.execute_fetchall(
        "SELECT COALESCE(SUM(amount), 0) as total FROM deals WHERE created_at BETWEEN ? AND ?",
        (start, end),
    )
    count = count_row[0]["cnt"]
    revenue = revenue_row[0]["total"]
    avg_deal = revenue / count if count > 0 else 0

    return {
        "count": count,
        "revenue": revenue,
        "avg_deal": avg_deal,
    }


async def get_today_stats() -> dict:
    today = datetime.now().strftime("%Y-%m-%d 00:00:00")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    return await get_stats_for_period(today, tomorrow)


async def get_week_stats() -> dict:
    now = datetime.now()
    start = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d 00:00:00")
    end = (now + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    return await get_stats_for_period(start, end)


async def get_month_stats() -> dict:
    now = datetime.now()
    start = now.replace(day=1).strftime("%Y-%m-%d 00:00:00")
    end = (now + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    return await get_stats_for_period(start, end)


async def get_all_time_stats() -> dict:
    db = await get_db()
    count_row = await db.execute_fetchall("SELECT COUNT(*) as cnt FROM deals")
    revenue_row = await db.execute_fetchall(
        "SELECT COALESCE(SUM(amount), 0) as total FROM deals"
    )
    count = count_row[0]["cnt"]
    revenue = revenue_row[0]["total"]
    avg_deal = revenue / count if count > 0 else 0
    return {"count": count, "revenue": revenue, "avg_deal": avg_deal}
