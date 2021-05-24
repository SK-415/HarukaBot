from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.typing import T_State

from ...database import Config
from ...utils import to_me


permission_on = on_command('开启权限', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, 
    priority=5)

@permission_on.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    with Config(event) as config:
        msg = await config.set_permission(True)
    await permission_on.finish(msg.replace('name', '开启权限'))