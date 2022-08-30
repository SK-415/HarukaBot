from nonebot import on_command
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.params import ArgPlainText
from nonebot.permission import SUPERUSER

from ... import config
from ...database import DB as db
from ...utils import group_only, handle_uid, to_me, uid_check

at_off = on_command(
    "关闭全体", rule=to_me(), permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, priority=5
)
at_off.__doc__ = """关闭全体 UID"""

at_off.handle()(group_only)
at_off.handle()(handle_uid)
at_off.got("uid", prompt="请输入要关闭全体的UID")(uid_check)


@at_off.handle()
async def _(event: GroupMessageEvent, uid: str = ArgPlainText("uid")):
    """根据 UID 关闭全体"""
    if await db.set_sub("at", False, uid=uid, type="group", type_id=event.group_id):
        user = await db.get_user(uid=uid)
        assert user is not None
        await at_off.finish(
            f"已关闭 {user.name}（{user.uid}）"
            f"{'直播推送' if not config.haruka_dynamic_at else ''}的@全体"
        )
    await at_off.finish(f"UID（{uid}）未关注，请先关注后再操作")
