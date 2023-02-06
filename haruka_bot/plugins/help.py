from nonebot.matcher import matchers

from ..utils import on_command, to_me
from ..version import __version__

help = on_command("帮助", rule=to_me(), priority=5)


@help.handle()
async def _():
    message = "HarukaBot目前支持的功能：\n（请将UID替换为需要操作的B站UID）\n"
    for matchers_list in matchers.values():
        for matcher in matchers_list:
            if (
                matcher.plugin_name
                and matcher.plugin_name.startswith("haruka_bot")
                and matcher.__doc__
            ):
                message += matcher.__doc__ + "\n"
    message += f"\n当前版本：v{__version__}\n" "详细帮助：https://haruka-bot.sk415.icu/usage/"
    await help.finish(message)
