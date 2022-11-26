from typing import Union

from nonebot.adapters.onebot.v11 import Bot
from nonebot.exception import FinishedException
from nonebot_plugin_guild_patch import GuildMessageEvent


async def permission_check_guild_admin(bot: Bot, event: Union[GuildMessageEvent]):
    if not await if_haruka_guild_admin(bot, event):
        await bot.send(event, "权限不足，目前只有管理员才能使用")
        raise FinishedException


async def if_haruka_guild_admin(bot, event):
    # from ..database import DB as db
    # guild_admin_list = await db.get_guild_admin_sub_list()

    # 初始化数据库中管理员ID列表
    # guild_admin_uid_list = []

    # 数据库中的用户列表
    # for guild_admin in guild_admin_list:
    #     guild_admin_uid_list.append(guild_admin.guild_admin_uid)

    # 判断是否为超级用户
    if str(event.user_id) in await get_super_user_list(bot):
        return True

    # 判断是否在数据库表中
    # elif str(event.user_id) in guild_admin_uid_list:
    #     return True

    # 判断是否为管理员身份组
    if await if_haruka_guild_admin_group(bot=bot, event=event):
        return True
    return False


async def if_haruka_guild_admin_group(bot, event: GuildMessageEvent):
    guild_member_info = await get_guild_member_info(bot, event.guild_id, event.user_id)
    for per_role in guild_member_info["roles"]:
        if per_role["role_name"] in await get_haruka_guild_admin_group_list(bot):
            return True
    return False


async def get_guild_member_info(bot, guild_id, user_id):
    return await bot.call_api(
        "get_guild_member_profile", guild_id=guild_id, user_id=user_id
    )


# 配置文件中管理员身份组
async def get_haruka_guild_admin_group_list(bot: Bot):
    try:
        return bot.config.haruka_guild_admin_group_list
    except AttributeError:
        return []


# 配置文件超级用户
async def get_super_user_list(bot: Bot):
    try:
        return bot.config.superusers
    except AttributeError:
        return []
