from typing import List, Union, Optional, Iterable
from tokeneff.core.translation.languages import Language

try:
    from googletrans import Translator
except ImportError:
    print(
        "⚠️ googletrans module not found. Install it using:\n    pip install googletrans==4.0.0-rc1"
    )
    Translator = None

# Create global translator instance
_translator = Translator() if Translator is not None else None


def _ensure_translator():
    """Ensure googletrans is available."""
    if _translator is None:
        raise RuntimeError(
            "googletrans library is not available. "
            "Install with: pip install googletrans==4.0.0-rc1"
        )
    return _translator


def _normalize_input(text_or_list: Union[str, Iterable[str]]):
    """Normalize input into list form."""
    if isinstance(text_or_list, str):
        return [text_or_list], True

    return list(text_or_list), False


async def translate(
    text_or_list: Union[str, Iterable[str]],
    src: str = "auto",
    dest: Union[str, Language] = Language.CHINESE,
    *,
    raise_on_error: bool = False,
) -> Union[str, List[str]]:
    """
    Asynchronously translate text or list of texts to another language.

    Args:
        text_or_list: A single string or iterable of strings.
        src: Source language (default: auto-detect).
        dest: Destination language (Language enum or str, default: Language.CHINESE).
        raise_on_error: Raise exception if translation fails.

    Returns:
        Translated string or list of strings.
    """
    translator = _ensure_translator()
    texts, single = _normalize_input(text_or_list)

    # Resolve language enum or string
    if isinstance(dest, Language):
        dest_code = dest.value
    else:
        try:
            dest_code = Language.from_name(dest).value
        except Exception:
            dest_code = str(dest)

    try:
        # googletrans Translator.translate is a coroutine
        result = await translator.translate(texts, src=src, dest=dest_code)

        # Handle single or multiple translations
        if len(texts) == 1:
            if hasattr(result, "text"):
                translated = result.text
            elif isinstance(result, list):
                translated = result[0].text
            else:
                translated = str(result)
        else:
            translated = [r.text for r in result]

        return translated if not single else translated

    except Exception as e:
        if raise_on_error:
            raise
        # fallback: return original input
        return text_or_list
