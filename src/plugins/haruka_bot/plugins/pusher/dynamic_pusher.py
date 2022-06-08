import asyncio
import traceback
from datetime import datetime, timedelta

from bilireq.dynamic import get_user_dynamics
from nonebot.log import logger

from ... import config
from ...database import DB as db
from ...libs.dynamic import Dynamic
from ...utils import PROXIES, get_dynamic_screenshot, safe_send, scheduler

last_time = {}


@scheduler.scheduled_job("interval", seconds=config.haruka_interval, id="dynamic_sched")
async def dy_sched():
    """直播推送"""

    uid = await db.next_uid("dynamic")
    if not uid:
        return
    user = await db.get_user(uid=uid)
    assert user is not None
    name = user.name

    logger.debug(f"爬取动态 {name}（{uid}）")
    # 获取最近十二条动态
    dynamics = (await get_user_dynamics(uid, proxies=PROXIES)).get("cards", [])
    # config['uid'][uid]['name'] = dynamics[0]['desc']['user_profile']['info']['uname']
    # await update_config(config)

    if len(dynamics) == 0:  # 没有发过动态或者动态全删的直接结束
        return

    if uid not in last_time:  # 没有爬取过这位主播就把最新一条动态时间为 last_time
        dynamic = Dynamic(**dynamics[0])
        last_time[uid] = dynamic.time
        return

    dynamic = None
    for dynamic in dynamics[::-1]:  # 从旧到新取最近5条动态
        dynamic = Dynamic(**dynamic)
        if (
            dynamic.time > last_time[uid]
            and dynamic.time
            > datetime.now().timestamp() - timedelta(minutes=10).seconds
        ):
            logger.info(f"检测到新动态（{dynamic.id}）：{name}（{uid}）")
            image = None
            for _ in range(3):
                try:
                    image = await get_dynamic_screenshot(dynamic.url)
                    break
                except Exception:
                    logger.error("截图失败，以下为错误日志:")
                    logger.error(traceback.format_exc())
                await asyncio.sleep(0.1)
            if not image:
                logger.error("已达到重试上限，将在下个轮询中重新尝试")
            await dynamic.format(image)

            push_list = await db.get_push_list(uid, "dynamic")
            for sets in push_list:
                await safe_send(
                    bot_id=sets.bot_id,
                    send_type=sets.type,
                    type_id=sets.type_id,
                    message=dynamic.message,
                    at=bool(sets.at) and config.haruka_dynamic_at,
                )

            last_time[uid] = dynamic.time

    if dynamic:
        await db.update_user(uid, dynamic.name)
