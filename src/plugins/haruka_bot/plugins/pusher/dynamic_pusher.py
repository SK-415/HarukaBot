import asyncio
import traceback
from datetime import datetime, timedelta

from nonebot.log import logger

from ...libs.bilireq import BiliReq
from ...database import DB
from ...libs.dynamic import Dynamic
from ...utils import safe_send, scheduler, get_dynamic_screenshot

last_time = {}

@scheduler.scheduled_job('interval', seconds=10, id='dynamic_sched')
async def dy_sched():
    """直播推送"""

    async with DB() as db:
        uid = await db.next_uid('dynamic')
        if not uid:
            return
        user = await db.get_user(uid)
        assert user is not None
        name = user.name

    logger.debug(f'爬取动态 {name}（{uid}）')
    br = BiliReq()
    dynamics = (await br.get_user_dynamics(uid)).get('cards', []) # 获取最近十二条动态
    # config['uid'][uid]['name'] = dynamics[0]['desc']['user_profile']['info']['uname']
    # await update_config(config)

    if len(dynamics) == 0: # 没有发过动态或者动态全删的直接结束
        return

    if uid not in last_time: # 没有爬取过这位主播就把最新一条动态时间为 last_time
        dynamic = Dynamic(dynamics[0])
        last_time[uid] = dynamic.time
        return
    
    for dynamic in dynamics[4::-1]: # 从旧到新取最近5条动态
        dynamic = Dynamic(dynamic)
        if dynamic.time > last_time[uid] and dynamic.time > datetime.now().timestamp() - timedelta(minutes=10).seconds:
            logger.info(f"检测到新动态（{dynamic.id}）：{name}（{uid}）")
            image = None
            for _ in range(3):
                try:
                    image = await get_dynamic_screenshot(dynamic.url)
                    break
                except Exception as e:
                    logger.error("截图失败，以下为错误日志:")
                    logger.error(traceback(e))
                await asyncio.sleep(0.1)
            if not image:
                logger.error("已达到重试上限，将在下个轮询中重新尝试")
            await dynamic.format(image)

            async with DB() as db:
                push_list = await db.get_push_list(uid, 'dynamic')
                for sets in push_list:
                    await safe_send(sets.bot_id, sets.type, sets.type_id, dynamic.message)

            last_time[uid] = dynamic.time
    await DB.update_user(uid, dynamic.name) # type: ignore
