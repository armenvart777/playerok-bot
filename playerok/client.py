import asyncio
import json
import logging
import nodriver as uc
from config import settings

logger = logging.getLogger(__name__)

# Persisted query hashes (from Playerok Apollo API)
PERSISTED_QUERIES = {
    "deals": "c3b623b5fe0758cf91b2335ebf36ff65f8650a6672a792a3ca7a36d270d396fb",
    "userChats": "999f86b7c94a4cb525ed5549d8f24d0d24036214f02a213e8fd7cefc742bbd58",
    "chatMessages": "e8162a8500865f4bb18dbaacb1c4703823f74c1925a91a5103f41c2021f0557a",
}

# Viewer query (POST with full text — already works)
VIEWER_QUERY = """query viewer {
  viewer {
    id username email role hasFrozenBalance
    unreadChatsCounter isBlocked createdAt
    balance { id value frozen available }
    profile { id username rating }
  }
}"""


class PlayerokClient:
    def __init__(self):
        self._browser = None
        self._page = None
        self._connected = False
        self._username: str | None = None
        self._user_id: str | None = None
        self._lock = asyncio.Lock()

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def username(self) -> str | None:
        return self._username

    async def connect(self) -> bool:
        try:
            logger.info("Starting Chrome browser...")
            self._browser = await uc.start(
                headless=False,
                browser_executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            )
            self._page = await self._browser.get("https://playerok.com")
            await self._page.sleep(5)

            # Wait for anti-bot challenges (Cloudflare, DDoS-Guard)
            for attempt in range(5):
                title = await self._page.evaluate("document.title")
                logger.info(f"Page title: {title}")
                challenge_keywords = ["cloudflare", "ddos-guard", "ddos", "attention", "момент", "checking"]
                if any(kw in (title or "").lower() for kw in challenge_keywords):
                    logger.info(f"Anti-bot challenge detected ({title}), waiting...")
                    await self._page.sleep(8)
                    self._page = await self._browser.get("https://playerok.com")
                    await self._page.sleep(5)
                else:
                    break

            # Set token cookie via CDP (supports httpOnly)
            await self._page.send(uc.cdp.network.set_cookie(
                name="token",
                value=settings.PLAYEROK_TOKEN,
                domain=".playerok.com",
                path="/",
                secure=True,
                http_only=True,
            ))
            logger.info("Token cookie set via CDP")

            # Navigate to playerok.com to apply token
            await self._page.sleep(1)
            self._page = await self._browser.get("https://playerok.com")
            await self._page.sleep(7)

            # Check for challenge again after token set
            title = await self._page.evaluate("document.title")
            if "ddos" in (title or "").lower() or "guard" in (title or "").lower():
                logger.info("DDoS-Guard still active after token, waiting longer...")
                await self._page.sleep(15)
                self._page = await self._browser.get("https://playerok.com")
                await self._page.sleep(7)

            # Test connection (with retry)
            data = None
            for attempt in range(3):
                data = await self._graphql_post(VIEWER_QUERY)
                if data.get("data", {}).get("viewer"):
                    break
                logger.warning(f"Viewer query attempt {attempt + 1} failed, retrying...")
                await self._page.sleep(3)

            viewer = data.get("data", {}).get("viewer") if data else None
            if viewer:
                self._username = viewer.get("username")
                self._user_id = viewer.get("id")
                self._connected = True
                logger.info(f"Connected as: {self._username}")
                return True

            logger.error(f"Failed to get viewer data: {data}")
            return False

        except Exception as e:
            logger.error(f"Playerok connection failed: {e}", exc_info=True)
            return False

    async def _graphql_post(self, query: str, variables: dict | None = None) -> dict:
        """Send a GraphQL POST request with full query text."""
        async with self._lock:
            op_name = query.split("(")[0].split()[-1] if "(" in query else query.split("{")[0].split()[-1]
            payload = json.dumps({
                "operationName": op_name,
                "query": query,
                "variables": variables or {},
            })

            js = f"""
            fetch('https://playerok.com/graphql', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'apollo-require-preflight': 'true',
                    'apollographql-client-name': 'web',
                    'x-gql-op': '{op_name}'
                }},
                credentials: 'include',
                body: {json.dumps(payload)}
            }}).then(r => r.text())
            """
            try:
                result = await self._page.evaluate(js, await_promise=True)
                if result is None:
                    return {"error": "null response"}
                return json.loads(result)
            except Exception as e:
                logger.error(f"GraphQL POST request failed: {e}")
                return {"error": str(e)}

    async def _graphql_get(self, operation_name: str, variables: dict, hash_key: str | None = None) -> dict:
        """Send a GraphQL GET request with persisted query hash (Apollo)."""
        async with self._lock:
            key = hash_key or operation_name
            sha256 = PERSISTED_QUERIES[key]

            variables_json = json.dumps(variables)
            extensions_json = json.dumps({
                "persistedQuery": {"version": 1, "sha256Hash": sha256}
            })

            # Build URL params via JS URLSearchParams for proper encoding
            js = f"""
            (() => {{
                const params = new URLSearchParams();
                params.set('operationName', {json.dumps(operation_name)});
                params.set('variables', {json.dumps(variables_json)});
                params.set('extensions', {json.dumps(extensions_json)});
                return fetch('https://playerok.com/graphql?' + params.toString(), {{
                    method: 'GET',
                    headers: {{
                        'apollo-require-preflight': 'true',
                        'apollographql-client-name': 'web',
                        'x-gql-op': {json.dumps(operation_name)}
                    }},
                    credentials: 'include'
                }}).then(r => r.text());
            }})()
            """
            try:
                result = await self._page.evaluate(js, await_promise=True)
                if result is None:
                    return {"error": "null response"}
                parsed = json.loads(result)
                if "errors" in parsed:
                    logger.warning(f"GraphQL {operation_name} errors: {parsed['errors']}")
                return parsed
            except Exception as e:
                logger.error(f"GraphQL GET request failed ({operation_name}): {e}")
                return {"error": str(e)}

    async def get_balance(self) -> dict:
        data = await self._graphql_post(VIEWER_QUERY)
        if "error" in data:
            return {"error": data["error"], "value": 0, "available": 0, "frozen": 0, "pending_income": 0}
        viewer = data.get("data", {}).get("viewer", {})
        if not viewer:
            return {"error": "no viewer", "value": 0, "available": 0, "frozen": 0, "pending_income": 0}
        bal = viewer.get("balance", {})
        return {
            "value": bal.get("value", 0),
            "available": bal.get("available", 0),
            "frozen": bal.get("frozen", 0),
            "pending_income": 0,
        }

    async def get_deals(self, count: int = 24, direction: str | None = None):
        variables = {
            "pagination": {"first": count, "after": None},
            "filter": {"userId": self._user_id},
            "showForbiddenImage": True,
        }
        if direction:
            variables["filter"]["direction"] = direction

        data = await self._graphql_get("deals", variables)
        if "errors" in data:
            logger.error(f"Deals query errors: {data['errors']}")
            return []
        deals_data = data.get("data", {}).get("deals", {})
        edges = deals_data.get("edges", [])
        logger.debug(f"Got {len(edges)} deals from API")
        return [edge["node"] for edge in edges]

    async def get_chats(self, count: int = 24, chat_type: str | None = None):
        variables = {
            "pagination": {"first": count, "after": None},
            "filter": {"userId": self._user_id},
            "hasSupportAccess": False,
        }
        if chat_type:
            variables["filter"]["type"] = chat_type

        data = await self._graphql_get("userChats", variables)
        if "errors" in data:
            logger.error(f"Chats query errors: {data['errors']}")
            return []
        chats_data = data.get("data", {}).get("chats", {})
        edges = chats_data.get("edges", [])
        return [edge["node"] for edge in edges]

    async def get_chat_messages(self, chat_id: str, count: int = 24):
        variables = {
            "pagination": {"first": count, "after": None},
            "filter": {"chatId": chat_id},
            "hasSupportAccess": False,
            "showForbiddenImage": True,
        }
        data = await self._graphql_get("chatMessages", variables)
        if "errors" in data:
            logger.error(f"Chat messages query errors: {data['errors']}")
            return []
        messages_data = data.get("data", {}).get("chatMessages", {})
        edges = messages_data.get("edges", [])
        return [edge["node"] for edge in edges]

    async def disconnect(self):
        if self._browser:
            try:
                self._browser.stop()
            except Exception:
                pass
            self._connected = False
