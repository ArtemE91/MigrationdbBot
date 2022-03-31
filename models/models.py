import asyncio
import datetime
from enum import Enum
from typing import Optional, List

import sqlalchemy
import ormar
import databases
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine

from dependencies import DATABASE_URL


database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = create_async_engine(DATABASE_URL, echo=True)


class LifetimeEnum(Enum):
    day = 'day'
    up_to_a_week = 'up_to_a_week'
    up_to_a_month = 'up_to_a_month'
    up_to_a_three_months = 'up_to_a_three_months'
    up_to_a_six_months = 'up_to_a_six_months'
    more_then_six_months = 'more_then_six_months'


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class User(ormar.Model):

    class Meta(BaseMeta):
        tablename = "users"

    id: int = ormar.BigInteger(primary_key=True)
    tg_user_id: int = ormar.BigInteger(unique=True)
    first_name: Optional[str] = ormar.String(max_length=1024, nullable=True)
    last_name: Optional[str] = ormar.String(max_length=1024, nullable=True)
    is_bot: Optional[bool] = ormar.Boolean(nullable=True)
    language_code: Optional[str] = ormar.String(max_length=10, nullable=True)
    mention: Optional[str] = ormar.String(max_length=256, nullable=True)
    last_date_online: Optional[datetime.datetime] = ormar.DateTime(default=datetime.datetime.now(), nullable=True)


class Channel(ormar.Model):

    class Meta(BaseMeta):
        tablename = 'channels'

    id: int = ormar.BigInteger(primary_key=True)
    tg_channel_id: int = ormar.BigInteger(unique=True)
    title: str = ormar.String(max_length=256)
    name: str = ormar.String(max_length=100, unique=True)
    link: str = ormar.String(max_length=256, unique=True)


class Group(ormar.Model):

    class Meta(BaseMeta):
        tablename = "groups"

    id: int = ormar.BigInteger(primary_key=True)
    tg_group_id: int = ormar.BigInteger(unique=True)
    name: Optional[str] = ormar.String(max_length=256, nullable=True)
    channel: Optional[List[Channel]] = ormar.ManyToMany(
        Channel, unique=True, related_name="groups"
    )   # baned_channels


class UserChannel(ormar.Model):

    class Meta(BaseMeta):
        tablename = "user_channels"

    id: int = ormar.BigInteger(primary_key=True)
    channel: Channel = ormar.ForeignKey(Channel, related_name='user_channels')
    user: User = ormar.ForeignKey(User, related_name='users_channels')
    first_seen: Optional[datetime.datetime] = ormar.Date(default=datetime.datetime.now().date(), nullable=True)
    is_exit: bool = ormar.Boolean(default=False)
    date_exit: Optional[datetime.datetime] = ormar.Date(nullable=True)


class UserGroup(ormar.Model):

    class Meta(BaseMeta):
        tablename = "user_groups"

    id: int = ormar.BigInteger(primary_key=True)
    group: Group = ormar.ForeignKey(Group, related_name='user_groups')
    user: User = ormar.ForeignKey(User, related_name='users_groups')
    first_seen: Optional[datetime.datetime] = ormar.Date(default=datetime.datetime.now().date(), nullable=True)
    is_exit: bool = ormar.Boolean(default=False)
    date_exit: Optional[datetime.datetime] = ormar.Date(nullable=True)


class CountUserGroup(ormar.Model):

    class Meta(BaseMeta):
        tablename = "count_user_groups"

    id: int = ormar.BigInteger(primary_key=True)
    group: Group = ormar.ForeignKey(Group, related_name='count_user_groups')
    count: int = ormar.Integer(default=0)
    date_seen: datetime.datetime = ormar.DateTime(default=datetime.datetime.now())


class CountUserChannel(ormar.Model):

    class Meta(BaseMeta):
        tablename = "count_user_channels"

    id: int = ormar.BigInteger(primary_key=True)
    channel: Channel = ormar.ForeignKey(Channel, related_name='count_user_channels')
    count: int = ormar.Integer(default=0)
    date_seen: datetime.datetime = ormar.DateTime(default=datetime.datetime.now())


class LifetimeUserGroup(ormar.Model):

    class Meta(BaseMeta):
        tablename = "lifetime_user_groups"

    id: int = ormar.BigInteger(primary_key=True)
    lifetime_user: str = ormar.String(max_length=50, choices=list(LifetimeEnum))
    user_group: UserGroup = ormar.ForeignKey(UserGroup, related_name='lifetime_user_groups')


class LifetimeUserChannel(ormar.Model):

    class Meta(BaseMeta):
        tablename = "lifetime_user_channels"

    id: int = ormar.BigInteger(primary_key=True)
    lifetime_user: str = ormar.String(max_length=50, choices=list(LifetimeEnum))
    user_channel: UserChannel = ormar.ForeignKey(UserChannel, related_name='lifetime_user_channels')


async def connect_db():
    try:
        await database.connect()
    except Exception as e:
        logger.error("connect db error, res is  {}".format(e))
        await asyncio.sleep(3)
        asyncio.ensure_future(connect_db())

asyncio.get_event_loop().run_until_complete(connect_db())








