from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.params import ArgPlainText

from ... import config
from ...database import DB as db
from ...utils import handle_uid, to_me, uid_check

at_on = on_command(
    "开启全体",
    rule=to_me(),
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER,
    priority=5,
)
at_on.__doc__ = """开启全体 UID"""

at_on.handle()(handle_uid)

at_on.got("uid", prompt="请输入要开启全体的UID")(uid_check)


@at_on.handle()
async def _(event: Union[PrivateMessageEvent, GroupMessageEvent], uid: str = ArgPlainText("uid")):
    """根据 UID 开启全体"""

    if isinstance(event, PrivateMessageEvent):
        await at_on.finish("只有群里才能开启全体")
        return  # IDE 快乐行
    if await db.set_sub(
        "at", True, uid=uid, type="group", type_id=event.group_id
    ):
        user = await db.get_user(uid=uid)
        assert user is not None
        await at_on.finish(
            f"已开启 {user.name}（{user.uid}）"
            f"{'直播推送' if not config.haruka_dynamic_at else ''}的@全体"
        )
    await at_on.finish(f"UID（{uid}）未关注，请先关注后再操作")
