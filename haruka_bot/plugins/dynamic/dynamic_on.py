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

dynamic_on = on_command("开启动态", rule=to_me(), priority=5)
dynamic_on.__doc__ = """开启动态 UID"""

dynamic_on.handle()(permission_check)

dynamic_on.handle()(handle_uid)

dynamic_on.got("uid", prompt="请输入要开启动态的UID")(uid_check)


@dynamic_on.handle()
async def _(event: MessageEvent, uid: str = ArgPlainText("uid")):
    """根据 UID 开启动态"""
    if await db.set_sub(
        "dynamic",
        True,
        uid=uid,
        type=event.message_type,
        type_id=await get_type_id(event),
    ):
        user = await db.get_user(uid=uid)
        assert user is not None
        await dynamic_on.finish(f"已开启 {user.name}（{user.uid}）的动态推送")
    await dynamic_on.finish(f"UID（{uid}）未关注，请先关注后再操作")
