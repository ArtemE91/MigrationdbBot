import datetime

import aiogram
from aiogram.utils.exceptions import ChatNotFound, BadRequest
from loguru import logger
import asyncpg

from models import models as db_new
from models import models_old_db as db_old
import asyncio

from dependencies import bot, dp
from serialize import get_dict_user, ChannelDb, GroupDb


async def update_info_user():
    users_new = await db_new.User.objects.all()
    exclude_users = [v.tg_user_id for v in users_new]
    if exclude_users:
        users = await db_old.User.objects.exclude(id__in=exclude_users).all()
    else:
        users = await db_old.User.objects.all()
    for user in users:
        groups = await db_old.Group.objects.filter(members__id=user).all()
        for group in groups:
            try:
                user_info = await bot.get_chat_member(group.id, user.id)
            except aiogram.utils.exceptions.BadRequest as e:
                pass
            except aiogram.utils.exceptions.BotKicked as e:
                pass
            else:
                obj_user = get_dict_user(user_info.user)
                try:
                    await db_new.User.objects.create(**obj_user)
                except asyncpg.exceptions.UniqueViolationError as e:
                    pass
                except Exception as e:
                    logger.error(e)
                    logger.error(obj_user)
                else:
                    logger.success(obj_user)
                    break


async def update_channel():
    channels_new = await db_new.Channel.objects.all()
    exclude_channel = [v.tg_channel_id for v in channels_new]
    if exclude_channel:
        channels = await db_old.Channel.objects.exclude(id__in=exclude_channel).all()
    else:
        channels = await db_old.Channel.objects.all()
    for channel in channels:
        channel_obj = ChannelDb(**channel.dict()).dict()
        try:
            await db_new.Channel.objects.create(**channel_obj)
        except asyncpg.exceptions.UniqueViolationError as e:
            pass
        except Exception as e:
            logger.error(e)
        else:
            logger.success(channel.dict())


async def update_group():
    groups_new = await db_new.Group.objects.all()
    exclude_groups = [v.tg_group_id for v in groups_new]
    if groups_new:
        groups = await db_old.Group.objects.exclude(id__in=exclude_groups).all()
    else:
        groups = await db_old.Group.objects.all()
    for group in groups:
        try:
            group_obj = GroupDb(**group.dict()).dict(exclude_none=True)
            new_group = await db_new.Group.objects.create(**group_obj)
            banned_channels = await db_old.Channel.objects.filter(groups__id=new_group.tg_group_id).all()
            for old_channel in banned_channels:
                channel = await db_new.Channel.objects.get(tg_channel_id=old_channel.id)
                await new_group.channel.add(channel)
        except asyncpg.exceptions.UniqueViolationError as e:
            pass
        except Exception as e:
            logger.error(e)


async def update_user_channel():
    users = await db_old.User.objects.all()
    for user in users:
        channels = await db_old.Channel.objects.filter(subscribers__id=user).all()
        for channel in channels:
            try:
                user_info = await bot.get_chat_member(channel.id, user.id)
                is_exit = False
            except BadRequest as e:
                is_exit = True
            except aiogram.utils.exceptions.BotKicked as e:
                logger.error("Kick Channel")
            check_duplicate = await db_new.UserChannel.objects.filter(channel__tg_channel_id=channel.id, user__tg_user_id=user.id).all()
            if check_duplicate:
                continue
            try:
                new_channel = await db_new.Channel.objects.get(tg_channel_id=channel.id)
                new_user = await db_new.User.objects.get(tg_user_id=user.id)
            except Exception as e:
                logger.error(e)
            else:
                kwargs = dict(channel=new_channel, user=new_user, is_exit=is_exit)
                if is_exit:
                    kwargs['date_exit'] = datetime.datetime.now().date()
                if not is_exit:
                    await db_new.UserChannel.objects.create(**kwargs)
                    logger.success(kwargs)


async def update_user_group():
    users = await db_old.User.objects.all()
    for user in users:
        groups = await db_old.Group.objects.filter(members__id=user).all()
        for group in groups:
            try:
                user_info = await bot.get_chat_member(group.id, user.id)
                is_exit = False
            except BadRequest as e:
                is_exit = True
            except aiogram.utils.exceptions.BotKicked as e:
                logger.error("Kick Bot")
            check_duplicate = await db_new.UserGroup.objects.filter(group__tg_group_id=group.id, user__tg_user_id=user.id).all()
            if check_duplicate:
                continue
            try:
                new_group = await db_new.Group.objects.get(tg_group_id=group.id)
                new_user = await db_new.User.objects.get(tg_user_id=user.id)
            except Exception as e:
                logger.error(e)
            else:
                kwargs = dict(group=new_group, user=new_user, is_exit=is_exit)
                if is_exit:
                    kwargs['date_exit'] = datetime.datetime.now().date()
                if not is_exit:
                    await db_new.UserGroup.objects.create(**kwargs)
                    logger.success(kwargs)


@dp.errors_handler(exception=aiogram.utils.exceptions.RetryAfter)
async def update_count_user_group():
    groups = await db_new.Group.objects.all()
    for group in groups:
        try:
            count = await bot.get_chat_members_count(group.tg_group_id)
        except ChatNotFound:
            logger.error(f"ChatNotFound {group.tg_group_id}")
            await db_new.Group.objects.delete(tg_group_id=group.tg_group_id)
        except aiogram.utils.exceptions.BotKicked:
            logger.error(f"Kick Group {group.tg_group_id}")
            await db_new.Group.objects.delete(tg_group_id=group.tg_group_id)
        else:
            await db_new.CountUserGroup.objects.create(count=count, group=group)
            logger.success(f"group_id = {group.tg_group_id} {count=}")


@dp.errors_handler(exception=aiogram.utils.exceptions.RetryAfter)
async def update_count_channel_group():
    channels = await db_new.Channel.objects.all()
    for channel in channels:
        try:
            count = await bot.get_chat_members_count(channel.tg_channel_id)
        except ChatNotFound:
            logger.error(f"ChatNotFound {channel.tg_channel_id}")
            await db_new.Channel.objects.delete(tg_channel_id=channel.tg_channel_id)
        except aiogram.utils.exceptions.BotKicked:
            logger.error(f"Kick channel{channel.tg_channel_id}")
            await db_new.Channel.objects.delete(tg_channel_id=channel.tg_channel_id)
        else:
            await db_new.CountUserChannel.objects.create(count=count, channel=channel)
            logger.success(f"channel_id = {channel.tg_channel_id} {count=}")


async def get_users_to_group():
    groups = await db_new.Group.objects.all()
    for group in groups:
        users = await db_new.User.objects.prefetch_related("users_groups").filter(
            users_groups__group__tg_group_id=group.tg_group_id
        ).all()
        for i in users:
            logger.info(i)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(update_count_channel_group())

