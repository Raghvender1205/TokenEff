# TokenEff

A python package to convert data formats

## Usage
## Basic example 

```python
import asyncio
from tokeneff.formatters.toon_formatter import ToonFormatter

async def main():
    data = {
        "name": "Raghvender",
        "role": "Machine Learning Engineer"
    }

    fmt = ToonFormatter()
    result = await fmt.format(data)

    print("TOON Content:")
    print(result.content)
    print("Token Count:", result.token_count)

asyncio.run(main())
```

### Using Converter, Formatter
All format transformations start with a `Converter`, which normalizes input
into Python `dict`, and a Formatter, which produces the desired output format.

```python
import asyncio
from tokeneff.core.converters.json_converter import JsonConverter
from tokeneff.formatters.toon_formatter import ToonFormatter
from tokeneff.core.models import ConversionInput

async def main():
    raw = '{"name": "John", "age": 30}'
    conv = JsonConverter()
    fmt = ToonFormatter()

    normalized = conv.parse(
        ConversionInput(data=raw, format="json")
    )
    out = await fmt.format(normalized)

    print(out.content)
    print("Tokens:", out.token_count)

asyncio.run(main())
```

### Translate Output (TOON + Translation)
`TokenEff` supports optional async translation for more token optimization. For chinese-aware tokenizers, chinese can be more token-efficient for the same tasks.

Example
```python
import asyncio
from tokeneff.formatters.toon_formatter import ToonFormatter
from tokeneff.core.translation.languages import Language

async def main():
    data = {"title": "Hello World", "description": "This is an example."}

    fmt = ToonFormatter()
    out = await fmt.format(data, translate_to=Language.CHINESE)

    print("Translated TOON:")
    print(out.content)

asyncio.run(main())
```

### Checkout tokens saved
```python
from tokeneff.utils.metrics import token_savings

original = '{"name": "John", "age": 30}'
optimized = 'name:John,age:30'

savings = token_savings(original, optimized)
print(f"Token Savings: {savings:.2f}%")
```

### Using Options (indendation, delimiters, key folding)
As same as [toon-ts](https://github.com/johannschopplich/toon), this package has support for options

Usage Example
```python
out = await fmt.format(
    data,
    delimiter=",",
    indent=2,
    key_folding=True
)
```

Options include
| Option            | Description                                      |          |
| ----------------- | ------------------------------------------------ | -------- |
| `delimiter`       | Separator for arrays / tables (`,`, `\t`, `\r`, etc.) |
| `indent`          | Indentation spaces for nested TOON output        |          |
| `key_folding`     | Collapse nested objects into dotted keys         |          |
| `translate_to`    | Translate output to another language             |          |
| `strict_fallback` | Fallback output format on unsupported structures |          |


### TODOs
- Add Support for CSV, YAML, DataFrame etc.
- Add bidirectional Support (TOON -> JSON) etc.
- Correct TOON format implementation using [toon-ts](https://github.com/johannschopplich/toon)
- Add token savings summary
- Also, maybe a language converter to make it more efficient