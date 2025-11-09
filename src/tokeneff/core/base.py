from typing import Any
from abc import ABC, abstractmethod
from tokeneff.core.models import ConversionInput, ConversionOutput


class BaseConverter(ABC):
    """Base class for converting various formats into a normalized data structure"""

    @abstractmethod
    def parse(self, raw_input: ConversionInput) -> dict:
        """Parse and normalize input data into a dict or list"""
        pass


class BaseFormatter(ABC):
    """Base class for converting normalized data into a compact string representation"""

    @abstractmethod
    def format(self, data: Any, **options) -> ConversionOutput:
        """
        Format the normalized data into token-efficient output
        Accepts optional kwargs (`translate_to="chinese")
        """
        pass
