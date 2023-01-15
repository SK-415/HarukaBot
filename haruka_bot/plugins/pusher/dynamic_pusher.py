import asyncio
from datetime import datetime

from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
    EVENT_SCHEDULER_STARTED,
)
from bilireq.grpc.dynamic import grpc_get_user_dynamics
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import DynamicType
from grpc import StatusCode
from grpc.aio import AioRpcError
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.log import logger

from ... import config
from ...database import DB as db
from ...database import dynamic_offset as offset
from ...utils import get_dynamic_screenshot, safe_send, scheduler


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
    try:
        # 获取 UP 最新动态列表
        dynamics = (
            await grpc_get_user_dynamics(
                uid, timeout=config.haruka_dynamic_timeout, proxy=config.haruka_proxy
            )
        ).list
    except AioRpcError as e:
        if e.code() == StatusCode.DEADLINE_EXCEEDED:
            logger.error("爬取动态超时，将在下个轮询中重试")
            return
        raise

    if not dynamics:  # 没发过动态
        if uid in offset and offset[uid] == -1:  # 不记录会导致第一次发动态不推送
            offset[uid] = 0
        return
    # 更新昵称
    name = dynamics[0].modules[0].module_author.author.name

    if uid not in offset:  # 已删除
        return
    elif offset[uid] == -1:  # 第一次爬取
        if len(dynamics) == 1:  # 只有一条动态
            offset[uid] = int(dynamics[0].extend.dyn_id_str)
        else:  # 第一个可能是置顶动态，但置顶也可能是最新一条，所以取前两条的最大值
            offset[uid] = max(
                int(dynamics[0].extend.dyn_id_str), int(dynamics[1].extend.dyn_id_str)
            )
        return

    dynamic = None
    for dynamic in dynamics[::-1]:  # 动态从旧到新排列
        dynamic_id = int(dynamic.extend.dyn_id_str)
        if dynamic_id > offset[uid]:
            logger.info(f"检测到新动态（{dynamic_id}）：{name}（{uid}）")
            url = f"https://t.bilibili.com/{dynamic_id}"
            image = await get_dynamic_screenshot(dynamic_id)
            if image is None:
                logger.debug(f"动态不存在，已跳过：{url}")
                return

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
                f"{name} {type_msg.get(dynamic.card_type, type_msg[0])}：\n"
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
                    at=bool(sets.at) and config.haruka_dynamic_at,
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


if config.haruka_dynamic_interval == 0:
    scheduler.add_listener(
        dynamic_lisener,
        EVENT_JOB_EXECUTED
        | EVENT_JOB_ERROR
        | EVENT_JOB_MISSED
        | EVENT_SCHEDULER_STARTED,
    )
else:
    scheduler.add_job(
        dy_sched, "interval", seconds=config.haruka_dynamic_interval, id="dynamic_sched"
    )
