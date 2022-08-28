import asyncio
import sys
from pathlib import Path
from typing import Union

import httpx
import nonebot
from nonebot import require
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import (
    ActionFailed,
    Message,
    MessageEvent,
    MessageSegment,
    NetworkError,
)
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg, RawCommand
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule

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
    matcher: Matcher,
    command_arg: Message = CommandArg(),
):
    uid = command_arg.extract_plain_text().strip()
    if uid:
        matcher.set_arg("uid", command_arg)


async def uid_check(
    matcher: Matcher,
    uid: str = ArgPlainText("uid"),
):
    uid = uid.strip()
    if not uid.isdecimal():
        await matcher.finish("UID 必须为纯数字")
    matcher.set_arg("uid", Message(uid))


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


async def group_only(
    matcher: Matcher, event: MessageEvent, command: str = RawCommand()
):
    if not isinstance(event, GroupMessageEvent):
        await matcher.finish(f"只有群里才能{command}")


def to_me():
    if config.haruka_to_me:
        from nonebot.rule import to_me

        return to_me()

    async def _to_me() -> bool:
        return True

    return Rule(_to_me)


async def safe_send(bot_id, send_type, type_id, message, at=False):
    """发送出现错误时, 尝试重新发送, 并捕获异常且不会中断运行"""

    async def _safe_send(bot, send_type, type_id, message):
        return await bot.call_api(
            "send_" + send_type + "_msg",
            **{
                "message": message,
                "user_id" if send_type == "private" else "group_id": type_id,
            },
        )

    bots = nonebot.get_bots()
    bot = bots.get(str(bot_id))
    if bot is None:
        logger.error(f"推送失败，Bot（{bot_id}）未连接，尝试使用其他 Bot 推送")
        for bot_id, bot in bots.items():
            if (
                at
                and (await bot.get_group_at_all_remain(group_id=type_id))["can_at_all"]
            ):
                message = MessageSegment.at("all") + message
            try:
                result = await _safe_send(bot, send_type, type_id, message)
                logger.info(f"尝试使用 Bot（{bot_id}）推送成功")
                return result
            except Exception:
                continue
        logger.error(f"尝试失败，所有 Bot 均无法推送")
        return

    if at and (await bot.get_group_at_all_remain(group_id=type_id))["can_at_all"]:
        message = MessageSegment.at("all") + message

    try:
        return await _safe_send(bot, send_type, type_id, message)
    except ActionFailed as e:
        if e.info["msg"] == "GROUP_NOT_FOUND":
            from ..database import DB as db

            await db.delete_sub_list(type="group", type_id=type_id)
            await db.delete_group(id=type_id)
            logger.error(f"推送失败，群（{type_id}）不存在，已自动清理群订阅列表")
        elif e.info["msg"] == "SEND_MSG_API_ERROR":
            url = "https://haruka-bot.sk415.icu/usage/faq.html#机器人不发消息也没反应"
            logger.error(f"推送失败，账号可能被风控（{url}），错误信息：{e.info}")
        else:
            logger.error(f"推送失败，未知错误，错误信息：{e.info}")
    except NetworkError as e:
        logger.error(f"推送失败，请检查网络连接，错误信息：{e.msg}")


def get_type_id(event: MessageEvent):
    return event.group_id if isinstance(event, GroupMessageEvent) else event.user_id


def check_proxy():
    """检查代理是否有效"""
    if config.haruka_proxy:
        logger.info("检查代理是否有效")
        try:
            httpx.get(
                "https://icanhazip.com/",
                proxies={"all://": config.haruka_proxy},
                timeout=2,
            )
        except Exception:
            raise RuntimeError("加载失败，代理无法连接，请检查 HARUKA_PROXY 后重试")


def on_startup():
    """安装依赖并检查当前环境是否满足运行条件"""
    if config.fastapi_reload and sys.platform == "win32":
        raise ImportError("加载失败，Windows 必须设置 FASTAPI_RELOAD=false 才能正常运行 HarukaBot")
    try:  # 如果开启 realod 只在第一次运行
        asyncio.get_running_loop()
    except RuntimeError:
        from .browser import check_playwright_env, install

        check_proxy()
        install()
        asyncio.run(check_playwright_env())
        # 创建数据存储目录
        if not Path(get_path()).is_dir():
            Path(get_path()).mkdir(parents=True)


PROXIES = {"all://": config.haruka_proxy}

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from .browser import get_dynamic_screenshot  # noqa
