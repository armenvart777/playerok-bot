from datetime import datetime


def format_price(amount: float) -> str:
    if amount == int(amount):
        return f"{int(amount)} RUB"
    return f"{amount:.2f} RUB"


def format_dt(dt_str: str | None) -> str:
    if not dt_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        return str(dt_str)


def format_diff(diff: float) -> str:
    sign = "+" if diff >= 0 else ""
    return f"{sign}{format_price(diff)}"


def rating_stars(rating: int | None, max_stars: int = 5) -> str:
    if rating is None:
        return "N/A"
    filled = min(rating, max_stars)
    return "\u2b50" * filled + "\u2606" * (max_stars - filled)


def truncate(text: str, length: int = 100) -> str:
    if len(text) <= length:
        return text
    return text[:length - 3] + "..."
