from tokeneff.formatters.toon_formatter import ToonFormatter
from tokeneff.core.translation.languages import Language

import asyncio

async def main():
    fmt = ToonFormatter()
    sample = {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
        ],
        "tags": ["alpha", "beta"],
        "meta": {"count": 2, "desc": "Example"}
    }
    out = await fmt.format(sample, delimiter=",", indent=2, key_folding=False)
    print(out.content)
    print("tokens:", out.token_count)

if __name__ == '__main__':
    asyncio.run(main())