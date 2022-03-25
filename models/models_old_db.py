import asyncio
from typing import Optional, List

import databases
from loguru import logger
import ormar
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine

from dependencies import OLD_DATABASE_URL


database = databases.Database(OLD_DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = create_async_engine(OLD_DATABASE_URL, echo=True)


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Channel(ormar.Model):
    class Meta(BaseMeta):
        tablename = "channels"

    id: int = ormar.BigInteger(primary_key=True)
    title: str = ormar.String(max_length=256)
    name: str = ormar.String(max_length=100, unique=True)
    link: str = ormar.String(max_length=256, unique=True)


class Group(ormar.Model):
    class Meta(BaseMeta):
        tablename = "groups"

    id: int = ormar.BigInteger(primary_key=True)
    name: Optional[str] = ormar.String(max_length=256, nullable=True)
    baned_channels: Optional[List[Channel]] = ormar.ManyToMany(
        Channel, unique=True, related_name="groups"
    )


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"

    id: int = ormar.BigInteger(primary_key=True)
    subcriptions: Optional[List[Channel]] = ormar.ManyToMany(
        Channel, unique=True, related_name="subscribers"
    )
    groups: Optional[List[Group]] = ormar.ManyToMany(
        Group, unique=True, related_name="members"
    )


async def connect_db():
    try:
        await database.connect()
    except Exception as e:
        logger.error("connect db error, res is  {}".format(e))
        await asyncio.sleep(3)
        asyncio.ensure_future(connect_db())

asyncio.get_event_loop().run_until_complete(connect_db())
