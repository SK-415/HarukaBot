import asyncio
import traceback

from nonebot.log import logger
from nonebot.adapters.onebot.v11.message import MessageSegment

from ... import config
from ...database import DB as db
from ...libs.grpc import grpc_dyn_get
from ...libs.grpc.bilibili.app.dynamic.v2.dynamic_pb2 import DynamicType
from ...utils import get_dynamic_screenshot, safe_send, scheduler

OFFSET = {}


@scheduler.scheduled_job("interval", seconds=1, id="dynamic_sched")
async def dy_sched():
    """直播推送"""

    uid = await db.next_uid("dynamic")
    if not uid:
        return
    user = await db.get_user(uid=uid)
    assert user is not None
    name = user.name

    # 获取 up 个人主页
    user_dyn_page = await grpc_dyn_get(uid)
    dynamics = user_dyn_page.list
    if dynamics:
        # 如果 up 动态页正常则更新 up 名字
        name = dynamics[0].modules[0].module_author.author.name

    logger.debug(f"爬取动态 {name}（{uid}）")

    # config['uid'][uid]['name'] = dynamics[0]['desc']['user_profile']['info']['uname']
    # await update_config(config)

    if uid not in OFFSET:  # 没有爬取过这位主播就把最新一条动态时间为 last_time
        dynamic = dynamics[0]
        OFFSET[uid] = int(dynamic.extend.dyn_id_str)
        return

    dynamic = None
    for dynamic in dynamics[::-1]:  # 从旧到新取最近5条动态
        dyn_id = int(dynamic.extend.dyn_id_str)
        if dyn_id > OFFSET[uid]:
            logger.info(f"检测到新动态（{dyn_id}）：{name}（{uid}）")
            url = f"https://t.bilibili.com/{dyn_id}"
            image = None
            for _ in range(3):
                try:
                    image = await get_dynamic_screenshot(url)
                    break
                except Exception:
                    logger.error("截图失败，以下为错误日志:")
                    logger.error(traceback.format_exc())
                await asyncio.sleep(0.1)
            if not image:
                logger.error("已达到重试上限，将在下个轮询中重新尝试")

            type_msg = {
                0: "发布了新动态",
                DynamicType.forward: "转发了一条动态",
                DynamicType.word: "发布了新文字动态",
                DynamicType.draw: "发布了新图文动态",
                DynamicType.av: "发布了新投稿",
                DynamicType.article: "发布了新专栏",
                DynamicType.music: "发布了新音频",
            }
            message = (
                f"{name} "
                + f"{type_msg.get(dynamic.card_type, type_msg[0])}：\n"
                + f"{url}\n"
                + MessageSegment.image(f"base64://{image}")
            )

            push_list = await db.get_push_list(uid, "dynamic")
            for sets in push_list:
                await safe_send(
                    bot_id=sets.bot_id,
                    send_type=sets.type,
                    type_id=sets.type_id,
                    message=message,
                    at=bool(sets.at) and config.haruka_dynamic_at,
                )

            OFFSET[uid] = dyn_id

    if dynamic:
        await db.update_user(uid, name)
