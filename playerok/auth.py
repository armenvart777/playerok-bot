import asyncio
import logging
from playerokapi.account import Account

logger = logging.getLogger(__name__)

SETUP_GUIDE_TEXT = """
<b>Настройка Playerok (Mac)</b>

Для работы бота нужен <b>token</b> от Playerok и <b>User-Agent</b> браузера.

<b>Как получить token:</b>
1. Откройте <a href="https://playerok.com">playerok.com</a> в Chrome/Safari
2. Войдите в свой аккаунт
3. Откройте DevTools: <b>Cmd + Option + I</b>
4. Перейдите во вкладку <b>Application</b> (Chrome) или <b>Storage</b> (Safari)
5. Слева: <b>Cookies</b> → <b>https://playerok.com</b>
6. Найдите cookie с именем <b>token</b>
7. Скопируйте значение (Value)

<i>Safari: если вкладки нет, включите меню разработки:
Safari → Настройки → Дополнения → Показать меню «Разработка»
Затем: Разработка → Показать Web Inspector</i>

<b>Как получить User-Agent:</b>
1. В DevTools перейдите во вкладку <b>Network</b> (Сеть)
2. Обновите страницу (<b>Cmd + R</b>)
3. Нажмите на любой запрос в списке
4. В заголовках найдите <b>User-Agent</b>
5. Скопируйте всю строку

Затем добавьте оба значения в файл <code>.env</code>:
<code>PLAYEROK_TOKEN=ваш_токен</code>
<code>PLAYEROK_USER_AGENT=ваш_user_agent</code>

И перезапустите бота.
"""


async def validate_token(token: str, user_agent: str = "") -> bool:
    def _validate():
        try:
            acc = Account(token=token, user_agent=user_agent)
            result = acc.get()
            return result is not None and result.username is not None
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False

    return await asyncio.to_thread(_validate)
