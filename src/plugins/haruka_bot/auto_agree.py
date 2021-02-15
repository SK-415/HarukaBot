from nonebot import on_request
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp.permission import PRIVATE_FRIEND



friend_req = on_request(priority=5)

@friend_req.handle()
async def _(bot: Bot, event: Event, state: dict):
    if event.request_type == 'friend' and str(event.user_id) in bot.config.superusers:
        await bot.set_friend_add_request(flag=event.flag, approve=True)


group_invite = on_request(priority=5)

@group_invite.handle()
async def _(bot: Bot, event: Event, state: dict):
    if event.request_type == 'group' and event.sub_type == 'invite' and str(event.user_id) in bot.config.superusers:
        await bot.set_group_add_request(flag=event.flag, sub_type='invite', approve=True)