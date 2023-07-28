import asyncio
from datetime import datetime

from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
    EVENT_SCHEDULER_STARTED,
)
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import DynamicType
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.log import logger

from ...config import plugin_config
from ...database import DB as db
from ...database import dynamic_offset as offset
from ...utils import get_dynamic_screenshot, safe_send, scheduler, get_user_dynamics


async def dy_sched():
    """动态推送"""
    uid = await db.next_uid("dynamic")
    if not uid:
        # 没有订阅先暂停一秒再跳过，不然会导致 CPU 占用过高
        await asyncio.sleep(1)
        return
    user = await db.get_user(uid=uid)
    assert user is not None
    name = user.name

    logger.debug(f"爬取动态 {name}（{uid}）")
    # 获取 UP 最新动态列表
    dynamics: list = (
        await get_user_dynamics(
            uid,
            cookie=plugin_config.haruka_browser_cookie,
            ua=plugin_config.haruka_browser_ua,
            timeout=plugin_config.haruka_dynamic_timeout,
            proxy=plugin_config.haruka_proxy,
        )
    )["items"]

    if not dynamics:  # 没发过动态
        if uid in offset and offset[uid] == -1:  # 不记录会导致第一次发动态不推送
            offset[uid] = 0
        return
    # 更新昵称
    name = dynamics[0]["modules"]["module_author"]["name"]

    if uid not in offset:  # 已删除
        return
    elif offset[uid] == -1:  # 第一次爬取
        if len(dynamics) == 1:  # 只有一条动态
            offset[uid] = int(dynamics[0]["id_str"])
        else:  # 第一个可能是置顶动态，但置顶也可能是最新一条，所以取前两条的最大值
            offset[uid] = max(
                int(dynamics[0]["id_str"]), int(dynamics[1]["id_str"])
            )
        return

    dynamic = None
    for dynamic in sorted(dynamics, key=lambda x: int(x["id_str"])):  # 动态从旧到新排列
        dynamic_id = int(dynamic["id_str"])
        if dynamic_id > offset[uid]:
            logger.info(f"检测到新动态（{dynamic_id}）：{name}（{uid}）")
            image, err = await get_dynamic_screenshot(dynamic_id)
            url = f"https://t.bilibili.com/{dynamic_id}"
            if image is None:
                logger.debug(f"动态不存在，已跳过：{url}")
                return
            elif dynamic["type"] in [
                "DYNAMIC_TYPE_LIVE_RCMD",
                "DYNAMIC_TYPE_LIVE",
                "DYNAMIC_TYPE_AD",
                "DYNAMIC_TYPE_BANNER",
            ]:
                logger.debug(f"无需推送的动态 {dynamic['type']}，已跳过：{url}")
                offset[uid] = dynamic_id
                return

            type_msg = {
                0: "发布了新动态",
                "DYNAMIC_TYPE_FORWARD": "转发了一条动态",
                "DYNAMIC_TYPE_WORD": "发布了新文字动态",
                "DYNAMIC_TYPE_DRAW": "发布了新图文动态",
                "DYNAMIC_TYPE_AV": "发布了新投稿",
                "DYNAMIC_TYPE_ARTICLE": "发布了新专栏",
                "DYNAMIC_TYPE_MUSIC": "发布了新音频",
            }
            message = (
                f"{name} {type_msg.get(dynamic['type'], type_msg[0])}：\n"
                + str(f"动态图片可能截图异常：{err}\n" if err else "")
                + MessageSegment.image(image)
                + f"\n{url}"
            )

            push_list = await db.get_push_list(uid, "dynamic")
            for sets in push_list:
                await safe_send(
                    bot_id=sets.bot_id,
                    send_type=sets.type,
                    type_id=sets.type_id,
                    message=message,
                    at=bool(sets.at) and plugin_config.haruka_dynamic_at,
                )

            offset[uid] = dynamic_id

    if dynamic:
        await db.update_user(uid, name)


def dynamic_lisener(event):
    if hasattr(event, "job_id") and event.job_id != "dynamic_sched":
        return
    job = scheduler.get_job("dynamic_sched")
    if not job:
        scheduler.add_job(
            dy_sched, id="dynamic_sched", next_run_time=datetime.now(scheduler.timezone)
        )


if plugin_config.haruka_dynamic_interval == 0:
    scheduler.add_listener(
        dynamic_lisener,
        EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED | EVENT_SCHEDULER_STARTED,
    )
else:
    scheduler.add_job(
        dy_sched,
        "interval",
        seconds=plugin_config.haruka_dynamic_interval,
        id="dynamic_sched",
    )
