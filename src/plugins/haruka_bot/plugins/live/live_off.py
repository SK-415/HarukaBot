from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.typing import T_State

from ...database import DB as db
from ...utils import get_type_id, permission_check, to_me, handle_uid


live_off = on_command("关闭直播", rule=to_me(), priority=5)
live_off.__doc__ = """关闭直播 UID"""

live_off.handle()(permission_check)

live_off.handle()(handle_uid)


@live_off.got("uid", prompt="请输入要关闭直播的UID")
async def _(event: MessageEvent, state: T_State):
    """根据 UID 关闭直播"""

    if await db.set_sub(
        "live",
        False,
        uid=state["uid"],
        type=event.message_type,
        type_id=get_type_id(event),
    ):
        user = await db.get_user(uid=state["uid"])
        assert user is not None
        await live_off.finish(f"已关闭 {user.name}（{user.uid}）的直播推送")
    await live_off.finish(f"UID（{state['uid']}）未关注，请先关注后再操作")
