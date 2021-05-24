from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.typing import T_State

from ...database import Config
from ...utils import to_me


at_off = on_command('关闭全体', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, 
    priority=5)

@at_off.handle()
async def handle_first_recive(bot: Bot, event: MessageEvent, state: T_State):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@at_off.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    uid = state['uid']
    with Config(event) as config:
        msg = await config.set('at', uid, False)
    await at_off.finish(msg.replace('name', '关闭全体'))