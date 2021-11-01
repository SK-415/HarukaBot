from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State

from ...database import DB
from ...utils import get_type_id, permission_check, to_me, handle_uid_weibo

live_on = on_command('开启微博', rule=to_me(), priority=5)
live_on.__doc__ = """开启微博 UID WEIBO_UID"""

live_on.handle()(permission_check)

live_on.handle()(handle_uid_weibo)


@live_on.got('uid', prompt='请输入要开启微博的UID')
@live_on.got('weibo_id', prompt='请输入要开启微博的WEIBO_UID')
async def _(bot: Bot, event: MessageEvent, state: T_State):
    """根据 UID 开启微博"""

    async with DB() as db:
        if await db.set_sub('weibo', True, uid=state['uid'],
                            type_=event.message_type,
                            type_id=get_type_id(event)):
            user = await db.get_user(state['uid'])
            assert user is not None
            await db.set_weibo_id(int(state['weibo_id']), uid=state['uid'],
                                  type_=event.message_type,
                                  type_id=get_type_id(event))
            await live_on.finish(f"已开启 {user.name}（{user.uid}）的微博推送")
        await live_on.finish(f"UID（{state['uid']}）未关注，请先关注后再操作")
