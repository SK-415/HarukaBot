from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.params import ArgPlainText

from ...database import DB as db, DBGuild as db_guild
from ...utils import get_type_id, handle_uid, permission_check, to_me, uid_check
from ...utils.guild_utils import permission_check_guild_admin

live_off = on_command("关闭直播", rule=to_me(), priority=5)
live_off.__doc__ = """关闭直播 UID"""

live_off.handle()(permission_check_guild_admin or permission_check)

live_off.handle()(handle_uid)

live_off.got("uid", prompt="请输入要关闭直播的UID")(uid_check)


@live_off.handle()
async def _(event: MessageEvent, uid: str = ArgPlainText("uid")):
    """根据 UID 关闭直播"""
    if event.message_type == "guild":
        guild = await db_guild.get_guild_db_id(guild_id=event.guild_id, channel_id=event.channel_id)
        type_id = guild.id
    else:
        type_id = get_type_id(event)

    if await db.set_sub(
        "live",
        False,
        uid=uid,
        type=event.message_type,
        type_id=type_id,
    ):
        user = await db.get_user(uid=uid)
        assert user is not None
        await live_off.finish(f"已关闭 {user.name}（{user.uid}）的直播推送")
    await live_off.finish(f"UID（{uid}）未关注，请先关注后再操作")
