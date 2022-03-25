from typing import Union
from nonebot import on_command
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, PrivateMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER

from ...database import DB as db
from ...utils import to_me


permission_on = on_command(
    "开启权限",
    rule=to_me(),
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER,
    priority=5,
)
permission_on.__doc__ = """开启权限"""


@permission_on.handle()
async def _(event: Union[PrivateMessageEvent, GroupMessageEvent]):
    """开启当前群权限"""

    if isinstance(event, PrivateMessageEvent):
        await permission_on.finish("只有群里才能开启权限")
        return  # IDE 快乐行
    if await db.set_permission(event.group_id, True):
        await permission_on.finish("已开启权限，只有管理员和主人可以操作")
    await permission_on.finish("权限已经开启了，只有管理员和主人可以操作")
