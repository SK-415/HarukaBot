from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State

from ...database import DB
from ...utils import permission_check, to_me, get_type_id
from ...libs.bilireq import BiliReq, RequestError


add_sub = on_command('关注', aliases={'添加主播',}, rule=to_me(), priority=5)
add_sub.__doc__ = """关注 UID"""

add_sub.handle()(permission_check)

@add_sub.handle()
async def get_args(bot: Bot, event: MessageEvent, state: T_State):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@add_sub.got('uid', prompt='请输入要关注的UID')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    """根据 UID 订阅 UP 主"""

    uid = state['uid']
    async with DB() as db:
        user = await db.get_user(uid)
        name = user and user.name
    if not name:
        br = BiliReq()
        try:
            name = (await br.get_info(uid))['name']
        except RequestError as e:
            if e.code == -400 or e.code == -404:
                await add_sub.finish("UID不存在，注意UID不是房间号")
            elif e.code == -412:
                await add_sub.finish("操作过于频繁IP暂时被风控，请半小时后再尝试")
            else:
                await add_sub.finish(f"未知错误，请联系开发者反馈，错误内容：\n\
                                    {str(e)}")
    async with DB() as db:
        result = await db.add_sub(uid, event.message_type,
                                  get_type_id(event), event.self_id, name)
    if result:
        await add_sub.finish(f"已关注 {name}（{uid}）")
    await add_sub.finish(f"请勿重复关注 {name}（{uid}）")