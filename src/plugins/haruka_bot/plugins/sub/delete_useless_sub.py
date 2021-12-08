from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State
import json

from ...database import DB
from ...utils import get_type_id, permission_check, to_me, handle_uid

delete_useless_sub = on_command('清理订阅', aliases={'清理群', '清理', }, rule=to_me(), priority=5)
delete_useless_sub.__doc__ = """清理无效的群与订阅"""

delete_useless_sub.handle()(permission_check)

delete_useless_sub.handle()(handle_uid)


@delete_useless_sub.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    """清理无效的群与订阅"""
    group_json = await bot.get_group_info()
    group_json_str = json.dumps(group_json)
    group_dict = json.loads(group_json_str)
    state = 0

    async with DB() as db:
        group = await db.get_all_group()
        for group_info in group:
            for i in group_dict['data']:
                if group_info.id == i['group_id']:
                    state = 1
                    break
            if state != 1:
                await delete_useless_sub.send("删除群：", group.id)
                #       db.delete_sub_list('group', group.id)
            state = 0
        await delete_useless_sub.finish("清理完毕")
