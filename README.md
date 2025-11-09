# TokenEff

A python package to convert data formats

## Usage
Simple example to convert data

```python
import asyncio
from tokeneff.formatters.toon_formatter import ToonFormatter
from tokeneff.core.models import ConversionInput
from tokeneff.core.translation.languages import Language

async def main():
    data = {"name": "Raghvender", "role": "Machine Learning Engineer"}
    fmt = ToonFormatter()
    out = await fmt.format(data, translate_to=Language.CHINESE)
    print("Translated Content:", out.content)
    print("Token Count:", out.token_count)

asyncio.run(main())
```

### TODOs
- Add Support for CSV, YAML, DataFrame etc.
- Add bidirectional Support (TOON -> JSON) etc.
- Correct TOON format implementation using [toon-ts](https://github.com/johannschopplich/toon)
- Add token savings summary
- Also, maybe a language converter to make it more efficient