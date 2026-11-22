import asyncio
import logging
import httpx

from consumer import run_consumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def main() -> None:
    async with httpx.AsyncClient() as client:
        await run_consumer(client)


if __name__ == "__main__":
    asyncio.run(main())