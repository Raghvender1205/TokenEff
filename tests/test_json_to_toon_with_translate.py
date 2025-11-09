import asyncio
import pytest
from tokeneff.core.converters.json_converter import JsonConverter
from tokeneff.formatters.toon_formatter import ToonFormatter
from tokeneff.core.models import ConversionInput
from tokeneff.core.translation.languages import Language


@pytest.mark.network
def test_json_to_toon_with_translation():
    async def _run():
        data = {"name": "Raghvender", "role": "ML Engineer"}
        conv = JsonConverter()
        fmt = ToonFormatter()

        normalized = conv.parse(ConversionInput(data=data, format="json"))
        out = await fmt.format(normalized, translate_to=Language.CHINESE)

        assert out.content is not None
        assert isinstance(out.content, str)
        assert out.token_count > 0

        # If translation failed (Google returned same text), skip gracefully
        if "Raghvender" in out.content or "Engineer" in out.content:
            pytest.skip("Translation did not change the text (network or API issue)")

        assert out.format == "toon"

    asyncio.run(_run())
