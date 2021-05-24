from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State

from ...database import Config
from ...utils import permission_check, to_me


sub_list = on_command('订阅列表', aliases={'主播列表',}, rule=to_me(), priority=5)

sub_list.handle()(permission_check)

@sub_list.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    with Config(event) as config:
        await sub_list.finish(await config.uid_list())