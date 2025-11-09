import json
from tokeneff.core.base import BaseConverter
from tokeneff.core.models import ConversionInput


class JsonConverter(BaseConverter):
    """Converts JSON data into normalized python dict"""

    def parse(self, raw_input: ConversionInput) -> dict:
        if isinstance(raw_input.data, str):
            return json.loads(raw_input.data)

        return raw_input.data
