from db.engine import get_db

SCHEMA = """
CREATE TABLE IF NOT EXISTS deals (
    id              TEXT PRIMARY KEY,
    item_name       TEXT NOT NULL,
    item_id         TEXT,
    buyer_username  TEXT,
    buyer_id        TEXT,
    amount          REAL NOT NULL,
    status          TEXT NOT NULL,
    direction       TEXT NOT NULL DEFAULT 'sale',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS deal_status_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id     TEXT NOT NULL,
    old_status  TEXT,
    new_status  TEXT NOT NULL,
    changed_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (deal_id) REFERENCES deals(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id              TEXT PRIMARY KEY,
    chat_id         TEXT NOT NULL,
    sender_username TEXT,
    sender_id       TEXT,
    text            TEXT,
    is_system       INTEGER NOT NULL DEFAULT 0,
    received_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reviews (
    id              TEXT PRIMARY KEY,
    deal_id         TEXT,
    rating          INTEGER,
    text            TEXT,
    author_username TEXT,
    status          TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS balance_snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    balance     REAL NOT NULL,
    available   REAL NOT NULL DEFAULT 0,
    frozen      REAL NOT NULL DEFAULT 0,
    diff        REAL NOT NULL DEFAULT 0.0,
    recorded_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS notification_settings (
    key         TEXT PRIMARY KEY,
    enabled     INTEGER NOT NULL DEFAULT 1,
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bot_state (
    key     TEXT PRIMARY KEY,
    value   TEXT NOT NULL
);
"""

DEFAULT_SETTINGS = [
    ("notify_new_order", 1),
    ("notify_new_message", 1),
    ("notify_new_review", 1),
    ("notify_balance_change", 1),
    ("notify_deal_status", 1),
]


async def init_db():
    db = await get_db()
    await db.executescript(SCHEMA)
    for key, enabled in DEFAULT_SETTINGS:
        await db.execute(
            "INSERT OR IGNORE INTO notification_settings (key, enabled) VALUES (?, ?)",
            (key, enabled),
        )
    await db.commit()
