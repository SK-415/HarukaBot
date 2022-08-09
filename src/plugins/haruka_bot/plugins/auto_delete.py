from nonebot import on_notice
from nonebot.adapters.onebot.v11 import GroupDecreaseNoticeEvent

from ..database import DB as db

group_decrease = on_notice(priority=5)


@group_decrease.handle()
async def _(event: GroupDecreaseNoticeEvent):
    """退群时，自动删除该群订阅列表"""
    if event.self_id == event.user_id:
        await db.delete_sub_list(type="group", type_id=event.group_id)
        await db.delete_group(id=event.group_id)
