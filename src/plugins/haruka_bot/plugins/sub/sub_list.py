from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State

from ...database import DB
from ...utils import get_type_id, permission_check, to_me

sub_list = on_command('关注列表', aliases={'主播列表',}, rule=to_me(), priority=5)
sub_list.__doc__ = """关注列表"""

sub_list.handle()(permission_check)

@sub_list.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    """发送当前位置的订阅列表"""

    message = "关注列表（所有群/好友都是分开的）\n\n"
    async with DB() as db:
        subs = await db.get_sub_list(event.message_type, get_type_id(event))
        for sub in subs:
            user = await db.get_user(sub.uid)
            assert user is not None
            message += (
                f"{user.name}（{user.uid}）\n"
                f"直播{'1' if sub.live else '0'} "
                f"动态{'1' if sub.dynamic else '0'} "
                f"微博{'1' if sub.weibo else '0'} "
                f"全体{'1' if sub.at else '0'}\n"
            )
    await sub_list.finish(message)
