from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ConversionInput:
    """Unify data input model"""

    data: Any
    format: str  # e.g 'json', 'csv', 'yaml', 'dataframe'
    options: Optional[Dict[str, Any]] = None


@dataclass
class ConversionOutput:
    """Standardized output model"""

    content: str
    format: str
    token_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
