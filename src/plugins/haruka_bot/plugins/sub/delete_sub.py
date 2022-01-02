from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State

from ...database import DB
from ...utils import get_type_id, permission_check, to_me, handle_uid


delete_sub = on_command('取关', aliases={'删除主播',}, rule=to_me(), priority=5)
delete_sub.__doc__ = """取关 UID或UP名称"""

delete_sub.handle()(permission_check)

delete_sub.handle()(handle_uid)

@delete_sub.got('uid', prompt='请输入要取关的UID或UP名称')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    """根据 UID或UP名称 删除 UP 主订阅"""

    uid = state['uid']
    async with DB() as db:
        name = getattr(await db.get_user(uid), 'name', None)
        if name:
            result = await db.delete_sub(uid, event.message_type,
                                         get_type_id(event))
        else:
            result = False

    if result:
        await delete_sub.finish(f"已取关 {name}（{uid}）")
    await delete_sub.finish(f"UID（{uid}）未关注")
