import asyncio
from tokeneff.core.translation.translation import translate
from tokeneff.core.translation.languages import Language


async def main():
    text = "Hello, how are you?"
    translated = await translate(text, dest=Language.CHINESE)
    print(translated)


asyncio.run(main())
