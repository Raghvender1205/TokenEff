import logging
import math
import textwrap
from typing import Any, Dict, List, Optional

from tokeneff.core.base import BaseFormatter
from tokeneff.core.models import ConversionOutput
from tokeneff.utils.tokenizer_utils import count_tokens
from tokeneff.core.translation.languages import Language

try:
    from tokeneff.core.translation.translation import translate
except Exception:
    translate = None

logger = logging.getLogger(__name__)

class ToonFormatter(BaseFormatter):
    """
    Enhanced TOON formatter implementing:
        - tabular encoding for uniform arrays of objects
        - array length headers
        - indendation and newlines
        - escaping and quoting rules
        - configurable delimiter / indent / key folding
        - Async translation with batching
    """
    # Max characters per translation chunk (heuristic)
    TRANSLATE_CHUNK_SIZE = 4000

    async def format(self, data: dict, **options) -> ConversionOutput:
        """
        Format the normalized data into TOON
        Options:
            - delimiter: str, default: ","
            - indent: int spaces for nested levels (default: 2)
            - key_folding: bool (default False)
                * Fold single-key chains into dotted keys when safe
            - translate_to / translate: Language or str (optional)
            - strict_fallback: "json" | "compact" | None - If structure unsupported, fallback behaviour

        ```python
        >>> fmt = ToonFormater()
        >>> out = await fmt.format(data, translate_to=Language.CHINESE)
        ```
        """
        delimiter: str = options.get("delimiter", ",")
        indent: int = options.get("indent", 2)
        key_folding: bool = bool(options.get("key_folding", False))
        strict_fallback: Optional[str] = options.get("strict_fallback", None)

        def _is_primitive(v: Any) -> bool:
            return v is None or isinstance(v, (str, bool, int, float))
        
        def _valid_identifier(s: str) -> bool:
            # NOTE: Rule: starts with letter or underscore, contains letters/digits/underscore
            if not isinstance(s, str) or len(s) == 0:
                return False

            return s.replace("_", "a").isalnum() and (s[0].isalpha() or s[0] == "_")
        
        def _escape_and_quote_string(s: str) -> str:
            # characters that force quoting or escaping: delimiter, ':', '\n', '\r', '"'
            special_chars = {delimiter, ":", "\n", "\r", '"', "\\"}
            esc = s.replace("\\", "\\\\")
            # escape delimiter and colon and newline/carriage return
            esc = esc.replace(":", "\\:").replace(delimiter, "\\" + delimiter)
            esc = esc.replace("\n", "\\n").replace("\r", "\\r")
            # if there are leading/trailing spaces or any unsafe chars, quote
            needs_quote = (
                s.startswith(" ")
                or s.endswith(" ")
                or any(ch in s for ch in special_chars)
                or len(s) == 0
            )
            if needs_quote:
                # escape internal double quotes
                esc = esc.replace('"', '\\"')
                return f'"{esc}"'
            
            return esc
        
        def _compact_primitive(v: Any) -> str:
            if v is None:
                return "null"
            if isinstance(v, bool):
                return "true" if v else "false"
            if isinstance(v, int):
                return str(v)
            if isinstance(v, float):
                s = repr(v)
                # remove trailing .0
                if s.endswith('.0'):
                    s = s[:-2]

                return s
            
            return _escape_and_quote_string(v)
        
        def _is_uniform_array_of_primitives(arr: List[Any]) -> bool:
            return all(_is_primitive(x) for x in arr)
        
        def _is_uniform_array_of_objects(arr: List[Any]) -> bool:
            if not arr:
                return False
            if not all(isinstance(x, dict) for x in arr):
                return False

            # All items must have same keys
            keyset = set(arr[0].keys())
            if any(set(x.keys()) != keyset for x in arr):
                return False
            # And values for each item must be primitives
            for item in arr:
                for v in item.values():
                    if not _is_primitive(v):
                        return False
            
            return True
        
        def _fold_keys(obj: Any, prefix: Optional[str] = None) -> (str, Any): # type: ignore
            """
            If key_folding enabled and obj is nested single-key chains, 
            
            Return:
                (folded_key, value)
            If cannot fold, returns (prefix, old)
            """
            cur = obj
            keys = []
            while isinstance(cur, dict) and len(cur) == 1:
                k = next(iter(cur.keys()))
                if not _valid_identifier(k):
                    break
                keys.append(k)
                cur = cur[k]
            
            if prefix:
                keyname = f"{prefix}." + ".".join(keys) if keys else prefix
            else:
                keyname = ".".join(keys) if keys else None

            return keyname, cur

        def _compact(obj: Any, level: int = 0, parent_key: Optional[str] = None) -> str:
            sp = " " * (indent * level)
            # Objects
            if isinstance(obj, dict):
                lines: List[str] = []
                # Optionally fold single-key chains
                if key_folding:
                    folded_key, folded_val = _fold_keys(obj)
                    if folded_key and folded_val is not obj:
                        # folded_key becomes an effective "parent" and we continue formatting folded_val
                        return _compact({folded_key: folded_val}, level, parent_key)

                for k, v in obj.items():
                    # safe key escaping: keys should be safe identifiers in many examples, else quote
                    if isinstance(k, str) and _valid_identifier(k):
                        key_repr = k
                    else:
                        key_repr = _escape_and_quote_string(k)

                    if isinstance(v, list):
                        # handle lists specially to include length and possible tabular representation
                        if _is_uniform_array_of_objects(v):
                            # tabular form header: key[length]{f1,f2}:
                            length = len(v)
                            fields = list(v[0].keys())
                            header = f"{sp}{key_repr}[{length}]{{{','.join(fields)}}}"
                            rows = []
                            for item in v:
                                cells = [_compact_primitive(item[f]) for f in fields]
                                rows.append(" " * (indent * (level + 1)) + delimiter.join(cells))
                            lines.append(header)
                            lines.extend(rows)
                        elif _is_uniform_array_of_primitives(v):
                            # primitive list inline after header
                            length = len(v)
                            header = f"{sp}{key_repr}[{length}]: {delimiter.join(_compact_primitive(x) for x in v)}"
                            lines.append(header)
                        else:
                            # mixed or nested lists: expand each element with dash / nested handling
                            length = len(v)
                            lines.append(f"{sp}{key_repr}[{length}]:")
                            for el in v:
                                # represent each on its own line, prefixed with '- '
                                # primitive items become inline
                                if _is_primitive(el):
                                    lines.append(" " * (indent * (level + 1)) + "- " + _compact_primitive(el))
                                else:
                                    lines.append(" " * (indent * (level + 1)) + "- " + _compact(el, level + 2))

                    elif isinstance(v, dict):
                        lines.append(f"{sp}{key_repr}:")
                        # nested object -> increased level
                        nested = _compact(v, level + 1)
                        # if nested does not already contain leading spaces, indent it
                        nested_lines = nested.splitlines()
                        for ln in nested_lines:
                            if ln.strip() == "":
                                lines.append(" " * (indent * (level + 1)) + ln)
                            else:
                                lines.append(ln if ln.startswith(" " * (indent * (level + 1))) else " " * (indent * (level + 1)) + ln)
                    else:
                        # primitive
                        lines.append(f"{sp}{key_repr}: {_compact_primitive(v)}")

                return "\n".join(lines)

            # List at the top level
            if isinstance(obj, list):
                if _is_uniform_array_of_objects(obj):
                    length = len(obj)
                    fields = list(obj[0].keys())
                    header = f"{sp}[{length}]{{{','.join(fields)}}}:"
                    rows = []
                    for item in obj:
                        cells = [_compact_primitive(item[f]) for f in fields]
                        rows.append(" " * (indent * (level + 1)) + delimiter.join(cells))
                    return header + "\n" + "\n".join(rows)
                elif _is_uniform_array_of_primitives(obj):
                    return f"{sp}[{len(obj)}]: " + delimiter.join(_compact_primitive(x) for x in obj)
                else:
                    out_lines = [f"{sp}[{len(obj)}]:"]
                    for el in obj:
                        if _is_primitive(el):
                            out_lines.append(" " * (indent * (level + 1)) + "- " + _compact_primitive(el))
                        else:
                            out_lines.append(" " * (indent * (level + 1)) + "- " + _compact(el, level + 2))

                    return "\n".join(out_lines)

            # Primitives at the top level
            return _compact_primitive(obj)

        # Build content
        try:
            content = _compact(data)
        except Exception as e:
            logger.exception(f"Failed to compact data to TOON: {e}")
            if strict_fallback == "json":
                import json as _json

                content = _json.dumps(data, ensure_ascii=False)
            elif strict_fallback == "compact":
                # simple compact feedback (single-line)
                def _flat(o):
                    if isinstance(o, dict):
                        return ",".join(f"{k}:{_flat(v)}" for k, v in o.items())
                    if isinstance(o, list):
                        return "[" + ",".join(_flat(x) for x in 0) + "]"

                    return str(o)

                content = _flat(data)
            else:
                raise

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

            # chunking by characters to avoid huge requests
            pieces: List[str] = []
            text = content
            if len(text) <= self.TRANSLATE_CHUNK_SIZE:
                pieces = [text]
            else:
                # naive chunk split on size but keep line integrity where possible
                lines = text.splitlines(keepends=True)
                cur = ""
                for line in lines:
                    if len(cur) + len(line) > self.TRANSLATE_CHUNK_SIZE and cur:
                        pieces.append(cur)
                        cur = line
                    else:
                        cur += line
                if cur:
                    pieces.append(cur)

            translated_pieces: List[str] = []
            for piece in pieces:
                try:
                    translated = await translate(piece, dest=translate_to)
                    if isinstance(translated, list):
                        translated_pieces.append(translated[0])
                    else:
                        translated_pieces.append(translated)
                except Exception as e:
                    logger.warning("Translation chunk failed; using untranslated chunk. Error: %s", e)
                    translated_pieces.append(piece)
            content = "".join(translated_pieces)

        # token counting
        tokens = None
        try:
            tokens = count_tokens(content)
        except Exception:
            logger.exception("Token counting failed, leaving token_count as None")

        return ConversionOutput(
            content=content,
            format="toon",
            token_count=tokens
        )