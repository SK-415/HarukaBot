from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State

from ....database import DB as Config
from ....utils import permission_check, to_me


delete_sub = on_command('取关', aliases={'删除主播',}, rule=to_me(), priority=5)

delete_sub.handle()(permission_check)

@delete_sub.handle()
async def get_args(bot: Bot, event: MessageEvent, state: T_State):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@delete_sub.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    uid = state['uid']
    with Config(event) as config:
        await delete_sub.finish(await config.delete_uid(uid))
