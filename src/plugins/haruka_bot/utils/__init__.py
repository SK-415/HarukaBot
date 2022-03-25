from pathlib import Path
from typing import Union

import nonebot
from nonebot import require
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed, NetworkError
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule
from nonebot.typing import T_State

from .. import config


def get_path(*other):
    """获取数据文件绝对路径"""
    if config.haruka_dir:
        dir_path = Path(config.haruka_dir).resolve()
    else:
        dir_path = Path.cwd().joinpath("data")
        # dir_path = Path.cwd().joinpath('data', 'haruka_bot')
    return str(dir_path.joinpath(*other))


async def handle_uid(
    bot: Bot,
    event: MessageEvent,
    state: T_State,
    command_arg: Message = CommandArg(),
):
    uid = command_arg.extract_plain_text().strip()
    if not uid:
        return
    if uid.isdecimal():
        state["uid"] = uid
    else:
        await bot.send(event, "UID 必须为纯数字")
        raise FinishedException


async def permission_check(
    bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent]
):
    from ..database import DB as db

    if isinstance(event, PrivateMessageEvent):
        if event.sub_type == "group":  # 不处理群临时会话
            raise FinishedException
        return
    if await db.get_admin(event.group_id) and not await (
        GROUP_ADMIN | GROUP_OWNER | SUPERUSER
    )(bot, event):
        await bot.send(event, "权限不足，目前只有管理员才能使用")
        raise FinishedException


def to_me():
    if config.haruka_to_me:
        from nonebot.rule import to_me

        return to_me()

    async def _to_me() -> bool:
        return True

    return Rule(_to_me)


async def safe_send(bot_id, send_type, type_id, message, at=False):
    """发送出现错误时, 尝试重新发送, 并捕获异常且不会中断运行"""

    try:
        bot = nonebot.get_bots()[str(bot_id)]
    except KeyError:
        logger.error(f"推送失败，Bot（{bot_id}）未连接")
        return

    if at and (await bot.get_group_at_all_remain(group_id=type_id))["can_at_all"]:
        message = MessageSegment.at("all") + message

    try:
        return await bot.call_api(
            "send_" + send_type + "_msg",
            **{
                "message": message,
                "user_id" if send_type == "private" else "group_id": type_id,
            },
        )
    except ActionFailed as e:
        url = "https://haruka-bot.sk415.icu/usage/faq.html#机器人不发消息也没反应"
        logger.error(f"推送失败，账号可能被风控（{url}），错误信息：{e.info}")
    except NetworkError as e:
        logger.error(f"推送失败，请检查网络连接，错误信息：{e.msg}")


def get_type_id(event: MessageEvent):
    return event.group_id if isinstance(event, GroupMessageEvent) else event.user_id


scheduler = require("nonebot_plugin_apscheduler")
assert scheduler is not None
scheduler = scheduler.scheduler


# bot 启动时检查 src\data\haruka_bot\ 目录是否存在
if not Path(get_path()).is_dir():
    Path(get_path()).mkdir(parents=True)

from .browser import get_dynamic_screenshot  # noqa
