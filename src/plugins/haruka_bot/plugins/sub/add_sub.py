from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.typing import T_State

from ...database import DB
from ...utils import permission_check, to_me, get_type_id, handle_uid
from bilireq.user import get_user_info
from bilireq.exceptions import ResponseCodeError


add_sub = on_command("关注", aliases={"添加主播"}, rule=to_me(), priority=5)
add_sub.__doc__ = """关注 UID"""

add_sub.handle()(permission_check)

add_sub.handle()(handle_uid)


@add_sub.got("uid", prompt="请输入要关注的UID")
async def _(event: MessageEvent, state: T_State):
    """根据 UID 订阅 UP 主"""

    uid = state["uid"]
    async with DB() as db:
        user = await db.get_user(uid)
        name = user and user.name
    if not name:
        try:
            name = (await get_user_info(uid, reqtype="web"))['name']
        except ResponseCodeError as e:
            if e.code == -400 or e.code == -404:
                await add_sub.finish("UID不存在，注意UID不是房间号")
            elif e.code == -412:
                await add_sub.finish("操作过于频繁IP暂时被风控，请半小时后再尝试")
            else:
                await add_sub.finish(
                    f"未知错误，请联系开发者反馈，错误内容：\n\
                                    {str(e)}"
                )
    async with DB() as db:
        result = await db.add_sub(
            uid, event.message_type, get_type_id(event), event.self_id, name
        )
    if result:
        await add_sub.finish(f"已关注 {name}（{uid}）")
    await add_sub.finish(f"{name}（{uid}）已经关注了")
