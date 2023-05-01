from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.params import ArgPlainText

from ...database import DB as db
from ...utils import (
    get_type_id,
    handle_uid,
    on_command,
    permission_check,
    to_me,
    uid_check,
)

live_off = on_command("关闭直播", rule=to_me(), priority=5)
live_off.__doc__ = """关闭直播 UID"""

live_off.handle()(permission_check)

live_off.handle()(handle_uid)

live_off.got("uid", prompt="请输入要关闭直播的UID")(uid_check)


@live_off.handle()
async def _(event: MessageEvent, uid: str = ArgPlainText("uid")):
    """根据 UID 关闭直播"""
    if await db.set_sub(
        "live",
        False,
        uid=uid,
        type=event.message_type,
        type_id=await get_type_id(event),
    ):
        user = await db.get_user(uid=uid)
        assert user is not None
        await live_off.finish(f"已关闭 {user.name}（{user.uid}）的直播推送")
    await live_off.finish(f"UID（{uid}）未关注，请先关注后再操作")
