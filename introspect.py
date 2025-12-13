"""One-shot script: introspect Playerok GraphQL to find correct field names."""
import asyncio
import json
import nodriver as uc
from config import settings

INTROSPECT_USER_FIELDS = """query IntrospectUser {
  __type(name: "User") {
    name
    fields {
      name
      type { name kind ofType { name kind ofType { name kind } } }
      args { name type { name kind ofType { name kind } } }
    }
  }
}"""

INTROSPECT_QUERY_FIELDS = """query IntrospectQuery {
  __type(name: "Query") {
    name
    fields {
      name
      type { name kind ofType { name kind } }
    }
  }
}"""


async def main():
    ...


asyncio.run(main())
