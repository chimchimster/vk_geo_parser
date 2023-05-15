import asyncio

from parser.parser import Query1, Query2, Query3


async def main():
    await asyncio.gather(
        Query1.fill_collection(),
        Query2.fill_collection(),
        Query3.fill_collection(),
    )

asyncio.run(main())