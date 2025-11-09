from enum import Enum


class Language(str, Enum):
    """Supported target languages for translations"""

    CHINESE = "zh-cn"
    ENGLISH = "en"
    HINDI = "hi"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    KOREAN = "ko"
    RUSSIAN = "ru"
    ARABIC = "ar"
    PORTUGUESE = "pt"
    ITALIAN = "it"
    DUTCH = "nl"

    @classmethod
    def from_name(cls, name: str):
        name = name.strip().upper().replace(" ", "_")
        try:
            return cls[name]
        except KeyError:
            raise ValueError(
                f"Unsupported langauge: {name}. Supported {', '.join([l.name.lower() for l in cls])}"
            )
