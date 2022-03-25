from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
from ...database import DB as db
from ...utils import get_type_id, permission_check, to_me

sub_list = on_command("关注列表", aliases={"主播列表"}, rule=to_me(), priority=5)
sub_list.__doc__ = """关注列表"""

sub_list.handle()(permission_check)


@sub_list.handle()
async def _(event: MessageEvent):
    """发送当前位置的订阅列表"""
    message = "关注列表（所有群/好友都是分开的）\n\n"
    subs = await db.get_sub_list(event.message_type, get_type_id(event))
    for sub in subs:
        user = await db.get_user(uid=sub.uid)
        assert user is not None
        message += (
            f"{user.name}（{user.uid}）"
            f"直播：{'开' if sub.live else '关'}，"
            f"动态：{'开' if sub.dynamic else '关'}，"
            # TODO 私聊不显示全体
            f"全体：{'开' if sub.at else '关'}\n"
            )
    await sub_list.finish(message)
