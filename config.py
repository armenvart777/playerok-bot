import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = field(default_factory=list)

    PLAYEROK_TOKEN: str = os.getenv("PLAYEROK_TOKEN", "")
    PLAYEROK_USER_AGENT: str = os.getenv("PLAYEROK_USER_AGENT", "")

    BALANCE_POLL_INTERVAL: int = int(os.getenv("BALANCE_POLL_INTERVAL", "60"))
    DEALS_POLL_INTERVAL: int = int(os.getenv("DEALS_POLL_INTERVAL", "30"))

    DB_PATH: str = os.getenv("DB_PATH", "data/monitor.db")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def __post_init__(self):
        raw = os.getenv("ADMIN_IDS", "")
        self.ADMIN_IDS = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]


settings = Settings()
