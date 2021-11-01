from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp import MessageEvent, MessageSegment
from nonebot.typing import T_State
from nonebot.log import logger

from ...database import DB
from ...utils import get_type_id, permission_check, to_me, handle_uid

echo = on_command('还能说话吗', rule=to_me(), priority=5)

@echo.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    message = MessageSegment.at(event.user_id) + "还能说话吗"
    await echo.finish(message)
