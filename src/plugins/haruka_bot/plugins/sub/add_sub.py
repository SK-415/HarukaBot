from bilireq.exceptions import ResponseCodeError
from bilireq.user import get_user_info
from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.typing import T_State
from src.plugins.nonebot_plugin_guild_patch import GuildMessageEvent
from ...GuildSuperUsers import GuildSuperUserList

from ...database import DB as db
from ...utils import PROXIES, get_type_id, handle_uid, permission_check, to_me

add_sub = on_command("关注", aliases={"添加主播"}, rule=to_me(), priority=5)
add_sub.__doc__ = """关注 UID"""

add_sub.handle()(permission_check)

add_sub.handle()(handle_uid)


@add_sub.got("uid", prompt="请输入要关注的UID")
async def _(event: MessageEvent, state: T_State):
    if isinstance(event, GuildMessageEvent):
        if str(event.user_id) in list(GuildSuperUserList):
            await add_uid(event=event,state=state)
        else:
            await add_sub.finish("您无权限进行此操作")
    else:
        await add_uid(event=event, state=state)


async def add_uid(event, state):
    """根据 UID 订阅 UP 主"""
    uid = state["uid"]
    user = await db.get_user(uid=uid)
    name = user and user.name
    if not name:
        try:
            name = (await get_user_info(uid, reqtype="web", proxies=PROXIES))["name"]
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
    result = await db.add_sub(
        uid=uid,
        type=event.message_type,
        type_id=get_type_id(event),
        bot_id=event.self_id,
        name=name,
        # TODO 自定义默认开关
        live=True,
        dynamic=True,
        at=False,
    )
    if result:
        await add_sub.finish(f"已关注 {name}（{uid}）")
    await add_sub.finish(f"{name}（{uid}）已经关注了")
