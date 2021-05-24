from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State

from ...database import DB
from ...utils import get_type_id, permission_check, to_me

sub_list = on_command('订阅列表', aliases={'主播列表',}, rule=to_me(), priority=5)
sub_list.__doc__ = """订阅列表"""

sub_list.handle()(permission_check)

@sub_list.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    """返回当前位置的订阅列表"""

    message = "以下为当前位置的订阅列表：\n\n"
    async with DB() as db:
        subs = await db.get_sub_list(event.message_type, get_type_id(event))
        for sub in subs:
            message += (
                f"【{(await db.get_user(sub.uid)).name}】" +
                f"直播推送：{'开' if sub.live else '关'}，" +
                f"动态推送：{'开' if sub.dynamic else '关'}" +
                f"（{sub.uid}）\n"
            )
    await sub_list.finish(message)
