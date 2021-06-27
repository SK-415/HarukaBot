from nonebot import on_notice
from nonebot.adapters.cqhttp import Bot, GroupDecreaseNoticeEvent
from nonebot.typing import T_State

from ..database import DB


group_decrease = on_notice(priority=5)

@group_decrease.handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent, state: T_State):
    """退群时，自动删除该群订阅列表"""

    if event.self_id == event.user_id:
        async with DB() as db:
            await db.delete_sub_list('group', event.group_id)
