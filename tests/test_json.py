import asyncio
from tokeneff.core.converters.json_converter import JsonConverter
from tokeneff.formatters.toon_formatter import ToonFormatter
from tokeneff.core.models import ConversionInput


def test_json_to_toon():
    async def _run():
        data = {"name": "Raghvender", "role": "ML Engineer"}
        conv = JsonConverter()
        fmt = ToonFormatter()
        normalized = conv.parse(ConversionInput(data=data, format="json"))
        out = await fmt.format(normalized)

        assert "name" in out.content
        assert out.token_count > 0

    asyncio.run(_run())
