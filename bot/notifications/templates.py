NEW_ORDER = """
\U0001f4e6 <b>\u041d\u043e\u0432\u044b\u0439 \u0437\u0430\u043a\u0430\u0437!</b>

\U0001f3ae \u0422\u043e\u0432\u0430\u0440: <b>{item_name}</b>
\U0001f464 \u041f\u043e\u043a\u0443\u043f\u0430\u0442\u0435\u043b\u044c: @{buyer}
\U0001f4b5 \u0421\u0443\u043c\u043c\u0430: <b>{amount} RUB</b>
\U0001f194 ID: <code>{deal_id}</code>
\U0001f552 \u0412\u0440\u0435\u043c\u044f: {time}
"""

NEW_MESSAGE = """
\U0001f4ac <b>\u041d\u043e\u0432\u043e\u0435 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435</b>

\U0001f464 \u041e\u0442: @{sender}
\U0001f4dd \u0422\u0435\u043a\u0441\u0442:
<i>{text}</i>
"""

NEW_REVIEW = """
\u2b50 <b>\u041d\u043e\u0432\u044b\u0439 \u043e\u0442\u0437\u044b\u0432</b>

\U0001f31f \u041e\u0446\u0435\u043d\u043a\u0430: {rating}
\U0001f464 \u041e\u0442: @{author}
\U0001f3ae \u0422\u043e\u0432\u0430\u0440: {item_name}
\U0001f4dd \u0422\u0435\u043a\u0441\u0442:
<i>{text}</i>
"""

BALANCE_CHANGE = """
\U0001f4b0 <b>\u0411\u0430\u043b\u0430\u043d\u0441 \u0438\u0437\u043c\u0435\u043d\u0438\u043b\u0441\u044f</b>

\U0001f4c9 \u0411\u044b\u043b\u043e: {old_balance} RUB
\U0001f4c8 \u0421\u0442\u0430\u043b\u043e: <b>{new_balance} RUB</b>
{diff_icon} \u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435: <b>{diff}</b>
\U0001f4b3 \u0414\u043e\u0441\u0442\u0443\u043f\u043d\u043e: {available} RUB
"""

DEAL_STATUS_CHANGE = """
\U0001f504 <b>\u0421\u0442\u0430\u0442\u0443\u0441 \u0441\u0434\u0435\u043b\u043a\u0438 \u0438\u0437\u043c\u0435\u043d\u0451\u043d</b>

\U0001f194 ID: <code>{deal_id}</code>
\U0001f3ae \u0422\u043e\u0432\u0430\u0440: {item_name}
{old_status} \u27a1 <b>{new_status}</b>
"""

STATUS_LABELS = {
    "PAID": "\U0001f7e2 \u041e\u043f\u043b\u0430\u0447\u0435\u043d",
    "PENDING": "\u23f3 \u041e\u0436\u0438\u0434\u0430\u043d\u0438\u0435",
    "SENT": "\U0001f4e8 \u041e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d",
    "CONFIRMED": "\u2705 \u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043d",
    "CONFIRMED_AUTOMATICALLY": "\u2705 \u0410\u0432\u0442\u043e\u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043d",
    "ROLLED_BACK": "\u274c \u041e\u0442\u043c\u0435\u043d\u0451\u043d",
}
