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


at_off = on_command('关闭全体', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, 
    priority=5)
at_off.__doc__ = """关闭全体 UID或UP名称"""

at_off.handle()(handle_uid)

@at_off.got('uid', prompt='请输入要关闭全体的UID或UP名称')
async def _(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent],
            state: T_State):
    """根据 UID或UP名称 关闭全体"""

    if isinstance(event, PrivateMessageEvent):
        await at_off.finish("只有群里才能关闭全体")
        return # IDE 快乐行
    async with DB() as db:
        if await db.set_sub('at', False, uid=state['uid'], type_='group',
                            type_id=event.group_id):
            user = await db.get_user(state['uid'])
            assert user is not None
            await at_off.finish(f"已关闭 {user.name}（{user.uid}）直播推送的@全体")
        await at_off.finish(f"UID（{state['uid']}）未关注，请先关注后再操作")