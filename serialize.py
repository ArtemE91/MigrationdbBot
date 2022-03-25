import datetime
from typing import Optional

from pydantic import BaseModel, Field


values_user = ('id', 'first_name', 'last_name',
               'is_bot', 'language_code', 'mention')


def get_dict_user(user):
    data = {}
    for arg in values_user:
        if arg == 'id':
            data['tg_user_id'] = getattr(user, arg)
            continue
        value = getattr(user, arg)
        if value:
            data[arg] = getattr(user, arg)
    return data


class ChannelDb(BaseModel):
    tg_channel_id: int = Field(alias="id")
    title: str
    name: str
    link: str


class GroupDb(BaseModel):
    tg_group_id: int = Field(alias="id")
    name: Optional[str]
