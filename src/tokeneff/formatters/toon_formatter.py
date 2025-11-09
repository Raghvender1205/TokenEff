from tokeneff.core.base import BaseFormatter
from tokeneff.core.models import ConversionOutput
from tokeneff.utils.tokenizer_utils import count_tokens
from tokeneff.core.translation.languages import Language

try:
    from tokeneff.core.translation.translation import translate
except Exception:
    translate = None


class ToonFormatter(BaseFormatter):
    """Simple compact format with comma-seperated TOON representation"""

    async def format(self, data: dict, **options) -> ConversionOutput:
        """
        format and optionally translate the data

        ```python
        >>> fmt = ToonFormater()
        >>> out = await fmt.format(data, translate_to=Language.CHINESE)
        ```
        """

        # Flattens dicts
        def _compact(obj):
            if isinstance(obj, dict):
                return ",".join(f"{k}:{_compact(v)}" for k, v in obj.items())
            elif isinstance(obj, list):
                return "[" + ",".join(_compact(v) for v in obj) + "]"
            return str(obj)

        content = _compact(data)

        # Handle Optional translation
        translate_to = options.get("translate_to") or options.get("translate")
        if translate_to:
            if translate is None:
                raise RuntimeError(
                    "Translation not available. Install googletrans==4.0.0-rc1"
                )
            if isinstance(translate_to, str):
                try:
                    translate_to = Language.from_name(translate_to)
                except ValueError:
                    pass

            try:
                translated = await translate(content, dest=translate_to)
                if isinstance(translated, list):
                    content = translated[0]
                else:
                    content = translated
            except Exception as e:
                # Fallback to un-translated content
                print(f"⚠️ Translation failed: {e}")

        tokens = count_tokens(content)

        return ConversionOutput(content=content, format="toon", token_count=tokens)
