import asyncio
import pytest

from tokeneff.core.converters.json_converter import JsonConverter
from tokeneff.formatters.toon_formatter import ToonFormatter
from tokeneff.core.models import ConversionInput


# -----------------------------
# Helper to run async formatter
# -----------------------------
def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# -----------------------------
# 1. Basic: Flat dict
# -----------------------------
def test_simple_json_to_toon():
    data = {"name": "Raghvender", "role": "ML Engineer"}

    conv = JsonConverter()
    fmt = ToonFormatter()

    normalized = conv.parse(ConversionInput(data=data, format="json"))
    out = run_async(fmt.format(normalized))

    assert "name" in out.content
    assert "role" in out.content
    assert out.token_count > 0


# -----------------------------
# 2. Nested dict
# -----------------------------
def test_nested_json_to_toon():
    data = {
        "meta": {
            "user": {
                "id": 10,
                "active": True
            }
        }
    }

    normalized = JsonConverter().parse(ConversionInput(data=data, format="json"))
    out = run_async(ToonFormatter().format(normalized))

    assert "meta:" in out.content
    assert "user:" in out.content
    assert "id: 10" in out.content
    assert "active: true" in out.content


# -----------------------------
# 3. Primitive array
# -----------------------------
def test_array_of_primitives():
    data = {"tags": ["alpha", "beta", "gamma"]}

    normalized = JsonConverter().parse(ConversionInput(data=data, format="json"))
    out = run_async(ToonFormatter().format(normalized))

    assert "tags[3]" in out.content
    assert "alpha" in out.content
    assert "beta" in out.content


# -----------------------------
# 4. Uniform object-array → tabular TOON
# -----------------------------
def test_uniform_object_array_to_tabular():
    data = {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
        ]
    }

    normalized = JsonConverter().parse(ConversionInput(data=data, format="json"))
    out = run_async(ToonFormatter().format(normalized))

    # header
    assert "users[2]{id,name,role}" in out.content

    # rows
    assert "1,Alice,admin" in out.content
    assert "2,Bob,user" in out.content


# -----------------------------
# 5. Mixed arrays (fallback list mode)
# -----------------------------
def test_mixed_array():
    data = {"items": [1, {"a": 2}, 3]}

    normalized = JsonConverter().parse(ConversionInput(data=data, format="json"))
    out = run_async(ToonFormatter().format(normalized))

    # Should not be tabular
    assert "{a}" not in out.content

    # Should produce hyphen list lines
    assert "- 1" in out.content
    assert "- 3" in out.content


# -----------------------------
# 6. Key folding test
# -----------------------------
def test_key_folding():
    data = {"outer": {"inner": {"final": 123}}}

    normalized = JsonConverter().parse(ConversionInput(data=data, format="json"))
    out = run_async(ToonFormatter().format(normalized, key_folding=True))

    # Should fold into outer.inner.final: 123
    assert "outer.inner.final" in out.content
    assert "123" in out.content


# -----------------------------
# 7. Strict fallback: compact
# -----------------------------
def test_strict_fallback_compact():
    # deliberately break formatter by passing unsupported type
    class Weird:
        pass

    data = {"invalid": Weird()}

    normalized = JsonConverter().parse(ConversionInput(data=data, format="json"))
    out = run_async(ToonFormatter().format(normalized, strict_fallback="compact"))

    # Should fallback to simple compact JSON-ish
    assert "invalid:" in out.content


# -----------------------------
# 8. Token count is computed
# -----------------------------
def test_token_count_computed():
    data = {"hello": "world"}

    normalized = JsonConverter().parse(ConversionInput(data=data, format="json"))
    out = run_async(ToonFormatter().format(normalized))

    assert out.token_count is not None
    assert out.token_count > 0


# -----------------------------
# 9. Translation disabled (sanity)
# -----------------------------
def test_translation_not_used():
    data = {"greet": "hello"}

    normalized = JsonConverter().parse(ConversionInput(data=data, format="json"))
    out = run_async(ToonFormatter().format(normalized))

    assert "hello" in out.content  # raw unchanged
