from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.params import ArgPlainText

from ...database import DB as db
from ...utils import get_type_id, handle_uid_and_live_tips, permission_check, to_me, uid_check

live_tips = on_command("开播提示词", rule=to_me(), priority=5)
live_tips.__doc__ = """开播提示词 UID:提示词（留空则恢复默认）"""

live_tips.handle()(permission_check)

live_tips.handle()(handle_uid_and_live_tips)

live_tips.got("uid", prompt="请输入要设置开播提示词的UID")(uid_check)

@live_tips.handle()
async def _(event: MessageEvent, uid: str = ArgPlainText("uid"), live_tips_str: str = ArgPlainText("live_tips")):
    """设置 UID 的开播提示词"""
    if await db.set_sub(
        "live_tips",
        live_tips_str,
        uid=uid,
        type=event.message_type,
        type_id=get_type_id(event),
    ):
        user = await db.get_user(uid=uid)
        assert user is not None
        resp = f"已设置 {user.name}（{user.uid}）的开播提示词为:{live_tips_str}" if live_tips_str else f"已恢复 {user.name}（{user.uid}）的开播提示词为默认"
        await live_tips.finish(resp)
    await live_tips.finish(f"UID（{uid}）未关注，请先关注后再操作")
