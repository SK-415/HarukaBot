from typing import Union
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, PrivateMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.typing import T_State

from ...database import DB
from ...utils import to_me


permission_off = on_command('关闭权限', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, 
    priority=5)
permission_off.__doc__ = """关闭权限"""

@permission_off.handle()
async def _(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent],
            state: T_State):
    """关闭当前群权限"""
    
    if isinstance(event, PrivateMessageEvent):
        await permission_off.finish("只有群里才能关闭权限")
        return # IDE 快乐行
    async with DB() as db:
        if await db.set_permission(event.group_id, False):
            await permission_off.finish("已关闭权限，所有人均可操作")
        await permission_off.finish("权限已经关闭了，所有人均可操作")
