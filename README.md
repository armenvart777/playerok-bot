# Playerok Bot

Telegram-бот для автоматизации работы на маркетплейсе Playerok. Подключается к аккаунту через nodriver (браузерная автоматизация), мониторит баланс и сделки, отправляет уведомления в Telegram.

## Что умеет

- Подключение к Playerok через GraphQL с авторизацией через cookie
- Мониторинг баланса и новых сделок в реальном времени
- Уведомления в Telegram при изменениях
- Команды для просмотра статуса и баланса прямо в боте
- Хранение данных в SQLite

## Стек

- Python 3.11+
- aiogram 3 - Telegram Bot API
- nodriver - браузерная автоматизация (обход Cloudflare)
- aiosqlite - асинхронная SQLite
- python-dotenv - конфигурация

## Запуск

```bash
cp .env.example .env
# заполнить .env (BOT_TOKEN, PLAYEROK_TOKEN, ADMIN_IDS)
pip install -r requirements.txt
python main.py
```

PLAYEROK_TOKEN берётся из cookie `token` после входа на playerok.com.

<!-- 2025-10-29 -->

<!-- 2025-12-10 -->
