from nonebot import on_notice
from nonebot.adapters.cqhttp import Bot, GroupDecreaseNoticeEvent
from nonebot.typing import T_State

from ..database import DB as Config
from ..version import __version__


group_decrease = on_notice(priority=5)

@group_decrease.handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent, state: T_State):
    if event.self_id == event.user_id:
        event.message_type = 'group'
        c = Config(event)
        await c.delete_push_list()