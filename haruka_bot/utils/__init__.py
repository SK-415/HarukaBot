import asyncio
import sys
import re
import contextlib
import datetime
from pathlib import Path
from typing import Union
from bilireq.utils import get

import httpx
import nonebot
from nonebot import on_command as _on_command
from nonebot import require
from nonebot.adapters.onebot.v11 import (
    ActionFailed,
    Bot,
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
from nonebot.permission import SUPERUSER, Permission
from nonebot.rule import Rule

from ..config import plugin_config

require("nonebot_plugin_guild_patch")
from nonebot_plugin_guild_patch import ChannelDestroyedNoticeEvent, GuildMessageEvent  # noqa


def get_path(*other):
    """获取数据文件绝对路径"""
    if plugin_config.haruka_dir:
        dir_path = Path(plugin_config.haruka_dir).resolve()
    else:
        dir_path = Path.cwd().joinpath("data")
        # dir_path = Path.cwd().joinpath('data', 'haruka_bot')
    return str(dir_path.joinpath(*other))


async def handle_uid(
    matcher: Matcher,
    command_arg: Message = CommandArg(),
):
    if command_arg.extract_plain_text().strip():
        matcher.set_arg("uid", command_arg)


async def uid_check(
    matcher: Matcher,
    uid: str = ArgPlainText("uid"),
):
    uid = uid.strip()
    if extract := await uid_extract(uid):
        uid = extract
    else:
        await matcher.finish("未找到该 UP，请输入正确的 UP 群内昵称、UP 名、UP UID或 UP 首页链接")
    matcher.set_arg("uid", Message(uid))


async def b23_extract(text: str):
    if "b23.tv" not in text and "b23.wtf" not in text:
        return None
    if not (b23 := re.compile(r"b23.(tv|wtf)[\\/]+(\w+)").search(text)):
        return None
    try:
        url = f"https://b23.tv/{b23[2]}"
        for _ in range(3):
            with contextlib.suppress(Exception):
                resp = await httpx.AsyncClient().get(url, follow_redirects=True)
                break
        else:
            return None
        url = resp.url
        logger.debug(f"b23.tv url: {url}")
        return str(url)
    except TypeError:
        return None


async def search_user(keyword: str):
    """
    搜索用户
    """
    url = "https://api.bilibili.com/x/web-interface/search/type"
    data = {"keyword": keyword, "search_type": "bili_user"}
    resp = await get(url, params=data)
    logger.debug(resp)
    return resp


async def uid_extract(text: str):
    logger.debug(f"[UID Extract] Original Text: {text}")
    b23_msg = await b23_extract(text) if "b23.tv" in text else None
    message = b23_msg or text
    logger.debug(f"[UID Extract] b23 extract: {message}")
    pattern = re.compile("^[0-9]*$|bilibili.com/([0-9]*)")
    if match := pattern.search(message):
        logger.debug(f"[UID Extract] Digit or Url: {match}")
        match = match[1] or match[0]
        return str(match)
    elif message.startswith("UID:"):
        pattern = re.compile("^\\d+")
        if match := pattern.search(message[4:]):
            logger.debug(f"[UID Extract] UID: {match}")
            return str(match[0])
    else:
        text_u = text.strip(""""'“”‘’""")
        if text_u != text:
            logger.debug(f"[UID Extract] Text is a Quoted Digit: {text_u}")
        logger.debug(f"[UID Extract] Searching UID in BiliBili: {text_u}")
        resp = await search_user(text_u)
        logger.debug(f"[UID Extract] Search result: {resp}")
        if resp and resp["numResults"]:
            for result in resp["result"]:
                if result["uname"] == text_u:
                    logger.debug(f"[UID Extract] Found User: {result}")
                    return str(result["mid"])
        logger.debug("[UID Extract] No User found")


async def _guild_admin(bot: Bot, event: GuildMessageEvent):
    roles = {
        role["role_name"]
        for role in (
            await bot.get_guild_member_profile(guild_id=event.guild_id, user_id=event.user_id)
        )["roles"]
    }
    return bool(roles & set(plugin_config.haruka_guild_admin_roles))


GUILD_ADMIN: Permission = Permission(_guild_admin)


async def permission_check(
    bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent, GuildMessageEvent]
):
    from ..database import DB as db

    if isinstance(event, PrivateMessageEvent):
        if event.sub_type == "group":  # 不处理群临时会话
            raise FinishedException
        return
    if isinstance(event, GroupMessageEvent):
        if not await db.get_group_admin(event.group_id):
            return
        if await (GROUP_ADMIN | GROUP_OWNER | SUPERUSER)(bot, event):
            return
    elif isinstance(event, GuildMessageEvent):
        if not await db.get_guild_admin(event.guild_id, event.channel_id):
            return
        if await (GUILD_ADMIN | SUPERUSER)(bot, event):
            return
    await bot.send(event, "权限不足，目前只有管理员才能使用")
    raise FinishedException


async def group_only(matcher: Matcher, event: PrivateMessageEvent, command: str = RawCommand()):
    await matcher.finish(f"只有群里才能{command}")


def to_me():
    if plugin_config.haruka_to_me:
        from nonebot.rule import to_me

        return to_me()

    async def _to_me() -> bool:
        return True

    return Rule(_to_me)


def calc_time_total(t):
    t = int(t * 1000)
    if t < 5000:
        return f"{t} 毫秒"

    timedelta = datetime.timedelta(seconds=t // 1000)
    day = timedelta.days
    hour, mint, sec = tuple(int(n) for n in str(timedelta).split(",")[-1].split(":"))

    total = ""
    if day:
        total += f"{day} 天 "
    if hour:
        total += f"{hour} 小时 "
    if mint:
        total += f"{mint} 分钟 "
    if sec and not day and not hour:
        total += f"{sec} 秒 "
    return total


async def safe_send(bot_id, send_type, type_id, message, at=False):
    """发送出现错误时, 尝试重新发送, 并捕获异常且不会中断运行"""

    async def _safe_send(bot, send_type, type_id, message):
        if send_type == "guild":
            from ..database import DB as db

            guild = await db.get_guild(id=type_id)
            assert guild
            result = await bot.send_guild_channel_msg(
                guild_id=guild.guild_id,
                channel_id=guild.channel_id,
                message=message,
            )
        else:
            result = await bot.call_api(
                f"send_{send_type}_msg",
                **{
                    "message": message,
                    "user_id" if send_type == "private" else "group_id": type_id,
                },
            )
        return result

    bots = nonebot.get_bots()
    bot = bots.get(str(bot_id))
    if bot is None:
        logger.error(f"推送失败，Bot（{bot_id}）未连接，尝试使用其他 Bot 推送")
        for bot_id, bot in bots.items():
            if at and (
                send_type == "guild"
                or (await bot.get_group_at_all_remain(group_id=type_id))["can_at_all"]
            ):
                message = MessageSegment.at("all") + message
            try:
                result = await _safe_send(bot, send_type, type_id, message)
                logger.info(f"尝试使用 Bot（{bot_id}）推送成功")
                return result
            except Exception:
                continue
        logger.error("尝试失败，所有 Bot 均无法推送")
        return

    if at and (
        send_type == "guild"
        or (await bot.get_group_at_all_remain(group_id=type_id))["can_at_all"]
    ):
        message = MessageSegment.at("all") + message

    try:
        return await _safe_send(bot, send_type, type_id, message)
    except ActionFailed as e:
        if e.info["msg"] == "GROUP_NOT_FOUND":
            from ..database import DB as db

            await db.delete_sub_list(type="group", type_id=type_id)
            await db.delete_group(id=type_id)
            logger.error(f"推送失败，群（{type_id}）不存在，已自动清理群订阅列表")
        elif e.info["msg"] == "CHANNEL_NOT_FOUND":
            from ..database import DB as db

            guild = await db.get_guild(id=type_id)
            assert guild
            await db.delete_sub_list(type="guild", type_id=type_id)
            await db.delete_guild(id=type_id)
            logger.error(f"推送失败，频道（{guild.guild_id}|{guild.channel_id}）不存在，已自动清理频道订阅列表")
        elif e.info["msg"] == "SEND_MSG_API_ERROR":
            url = "https://haruka-bot.sk415.icu/usage/faq.html#机器人不发消息也没反应"
            logger.error(f"推送失败，账号可能被风控（{url}），错误信息：{e.info}")
        else:
            logger.error(f"推送失败，未知错误，错误信息：{e.info}")
    except NetworkError as e:
        logger.error(f"推送失败，请检查网络连接，错误信息：{e.msg}")


async def get_type_id(event: Union[MessageEvent, ChannelDestroyedNoticeEvent]):
    if isinstance(event, (GuildMessageEvent, ChannelDestroyedNoticeEvent)):
        from ..database import DB as db

        return await db.get_guild_type_id(event.guild_id, event.channel_id)
    return event.group_id if isinstance(event, GroupMessageEvent) else event.user_id


def check_proxy():
    """检查代理是否有效"""
    if plugin_config.haruka_proxy:
        logger.info("检查代理是否有效")
        try:
            httpx.get(
                "https://icanhazip.com/",
                proxies={"all://": plugin_config.haruka_proxy},
                timeout=2,
            )
        except Exception:
            raise RuntimeError("加载失败，代理无法连接，请检查 HARUKA_PROXY 后重试")


def on_startup():
    """安装依赖并检查当前环境是否满足运行条件"""
    if plugin_config.fastapi_reload and sys.platform == "win32":
        raise ImportError("加载失败，Windows 必须设置 FASTAPI_RELOAD=false 才能正常运行 HarukaBot")
    try:  # 如果开启 realod 只在第一次运行
        asyncio.get_running_loop()
    except RuntimeError:
        from .browser import check_playwright_env, install

        check_proxy()
        install()
        asyncio.get_event_loop().run_until_complete(check_playwright_env())
        # 创建数据存储目录
        if not Path(get_path()).is_dir():
            Path(get_path()).mkdir(parents=True)


def on_command(cmd, *args, **kwargs):
    return _on_command(plugin_config.haruka_command_prefix + cmd, *args, **kwargs)


PROXIES = {"all://": plugin_config.haruka_proxy}

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler  # noqa

from .browser import get_dynamic_screenshot  # noqa
