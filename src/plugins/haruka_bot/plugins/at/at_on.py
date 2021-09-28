from typing import Union
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import (GroupMessageEvent, MessageEvent,
                                           PrivateMessageEvent)
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.typing import T_State

from ...database import DB
from ...utils import to_me, handle_uid


at_on = on_command('开启全体', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, 
    priority=5)
at_on.__doc__ = """开启全体 UID"""

at_on.handle()(handle_uid)

@at_on.got('uid', prompt='请输入要开启全体的UID')
async def _(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent],
            state: T_State):
    """根据 UID 开启全体"""

    if isinstance(event, PrivateMessageEvent):
        await at_on.finish("只有群里才能开启全体")
        return # IDE 快乐行
    async with DB() as db:
        if await db.set_sub('at', True, uid=state['uid'], type_='group',
                            type_id=event.group_id):
            user = await db.get_user(state['uid'])
            assert user is not None
            await at_on.finish(f"已开启 {user.name}（{user.uid}）直播推送的@全体")
        await at_on.finish(f"UID（{state['uid']}）未关注，请先关注后再操作")