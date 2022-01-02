from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State
from nonebot.matcher import matchers

from ..utils import to_me
from ..version import __version__


help = on_command('帮助', rule=to_me(), priority=5)

@help.handle()
async def test(bot: Bot, event: MessageEvent, state: T_State):
    message = "HarukaBot目前支持的功能：\n（请将UID或UP名称替换为需要操作的B站UID或UP名称）\n"
    for matchers_list in matchers.values():
        for matcher in matchers_list:
            if (matcher.plugin_name and
                matcher.plugin_name.startswith("haruka_bot") and
                matcher.__doc__):
                message += matcher.__doc__ + '\n'
    message += (f"\n提示：使用UP名称操作时请确保输入尽量准确，若结果有误请换用B站UID操作\n\n当前版本：v{__version__}\n"
                "反馈&帮助群：629574472\n"
                "详细帮助：https://haruka-bot.sk415.icu/usage/")
    await help.finish(message)