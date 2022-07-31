from nonebot import on_request
from nonebot.adapters.onebot.v11 import Bot, FriendRequestEvent, GroupRequestEvent

friend_req = on_request(priority=5)


@friend_req.handle()
async def friend_agree(bot: Bot, event: FriendRequestEvent):
    if str(event.user_id) in bot.config.superusers:
        await bot.set_friend_add_request(flag=event.flag, approve=True)


group_invite = on_request(priority=5)


@group_invite.handle()
async def group_agree(bot: Bot, event: GroupRequestEvent):
    if event.sub_type == "invite" and str(event.user_id) in bot.config.superusers:
        await bot.set_group_add_request(
            flag=event.flag, sub_type="invite", approve=True
        )
