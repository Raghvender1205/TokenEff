from tokeneff.core.base import BaseFormatter
from tokeneff.core.models import ConversionOutput
from tokeneff.utils.tokenizer_utils import count_tokens

class ToonFormatter(BaseFormatter):
    """Simple compact format with comma-seperated TOON representation"""
    def format(self, data: dict) -> ConversionOutput:
        # Flattens dicts
        def _compact(obj):
            if isinstance(obj, dict):
                return ','.join(f"{k}:{_compact(v)}" for k, v in obj.items())
            elif isinstance(obj, list):
                return '[' + ','.join(_compact(v) for v in obj) + ']'
            return str(obj)

        content = _compact(data)
        tokens = count_tokens(content)

        return ConversionOutput(content=content, format="toon", token_count=tokens)