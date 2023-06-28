from nonebot.adapters.onebot.v11.event import MessageEvent

from ...database import DB as db
from ...utils import get_type_id, on_command, permission_check, to_me

from ..pusher.live_pusher import status

live_now = on_command("已开播", rule=to_me(), priority=5)
live_now.__doc__ = """已开播"""

live_now.handle()(permission_check)


@live_now.handle()
async def _(event: MessageEvent):
    """返回已开播的直播间"""
    subs = await db.get_sub_list(event.message_type, await get_type_id(event))
    if now_live := [sub for sub in subs if status.get(str(sub.uid)) == 1]:
        await live_now.finish(
            f"共有{len(now_live)}个主播正在直播：\n\n"
            + "\n".join([f"{await db.get_name(sub.uid)}（{sub.uid}）" for sub in now_live])
        )
    await live_now.finish("当前没有正在直播的主播")
