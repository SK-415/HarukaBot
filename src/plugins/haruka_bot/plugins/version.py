from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State

from ..utils import to_me
from ..version import __version__


get_version = on_command('版本信息', rule=to_me(), priority=5)

@get_version.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    message = f"当前 HarukaBot 版本：{__version__}\n" +\
        "\n使用中遇到问题欢迎加群反馈，\n" +\
        "群号：629574472\n" +\
        "\n常见问题：https://haruka-bot.live/usage/faq.html"
    await get_version.finish(message)