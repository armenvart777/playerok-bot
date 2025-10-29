from dataclasses import dataclass


@dataclass
class Deal:
    id: str
    item_name: str
    item_id: str | None
    buyer_username: str | None
    buyer_id: str | None
    amount: float
    status: str
    direction: str
    created_at: str
    updated_at: str


@dataclass
class Message:
    id: str
    chat_id: str
    sender_username: str | None
    sender_id: str | None
    text: str | None
    is_system: bool
    received_at: str


@dataclass
class Review:
    id: str
    deal_id: str | None
    rating: int | None
    text: str | None
    author_username: str | None
    status: str | None
    created_at: str


@dataclass
class BalanceSnapshot:
    id: int
    balance: float
    available: float
    frozen: float
    diff: float
    recorded_at: str
