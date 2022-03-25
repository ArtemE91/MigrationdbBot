import asyncio

from models.models import engine, metadata


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

asyncio.get_event_loop().run_until_complete(init_models())