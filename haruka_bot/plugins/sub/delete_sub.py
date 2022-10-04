from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.params import ArgPlainText

from ...database import DB as db, DBGuild as db_guild
from ...utils import get_type_id, handle_uid, permission_check, to_me, uid_check
from ...utils.guild_utils import permission_check_guild_admin

delete_sub = on_command("取关", aliases={"删除主播"}, rule=to_me(), priority=5)
delete_sub.__doc__ = """取关 UID"""

delete_sub.handle()(permission_check_guild_admin or permission_check)

delete_sub.handle()(handle_uid)

delete_sub.got("uid", prompt="请输入要取关的UID")(uid_check)


@delete_sub.handle()
async def _(event: MessageEvent, uid: str = ArgPlainText("uid")):
    """根据 UID 删除 UP 主订阅"""
    name = getattr(await db.get_user(uid=uid), "name", None)
    if name:
        if event.message_type == "guild":
            guild = await db_guild.get_guild_db_id(
                guild_id=event.guild_id,
                channel_id=event.channel_id,
            )
            print(guild.id)
            result = await db_guild.delete_guild_sub(
                uid=uid,
                type="guild",
                type_id=guild.id,
            )
        else:
            result = await db.delete_sub(
                uid=uid, type=event.message_type, type_id=get_type_id(event)
            )
    else:
        result = False

    if result:
        await delete_sub.finish(f"已取关 {name}（{uid}）")
    await delete_sub.finish(f"UID（{uid}）未关注")
