from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State

from ...database import DB
from ...utils import get_type_id, permission_check, to_me


live_off = on_command('关闭直播', rule=to_me(), priority=5)
live_off.__doc__ = """关闭直播 UID"""

live_off.handle()(permission_check)

@live_off.handle()
async def handle_first_recive(bot: Bot, event: MessageEvent, state: T_State):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@live_off.got('uid', prompt='请输入要关闭直播的UID')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    """根据 UID 关闭直播"""

    async with DB() as db:
        if await db.set_sub('live', False, uid=state['uid'],
                            type_=event.message_type,
                            type_id=get_type_id(event)):
            user = (await db.get_user(state['uid']))
            await live_off.finish(f"已关闭 {user.name}（{user.uid}）的直播推送")
        await live_off.finish(f"UID（{state['uid']}）未关注，请先关注后再操作")
