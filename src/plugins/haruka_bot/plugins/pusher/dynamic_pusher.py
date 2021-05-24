from datetime import datetime, timedelta

from nonebot.log import logger

from ...libs.bilireq import BiliReq
from ...database import DB
from ...libs.dynamic import Dynamic
from ...utils import safe_send, scheduler

last_time = {}

@scheduler.scheduled_job('interval', seconds=10, id='dynamic_sched')
async def dy_sched():
    """直播推送"""

    async with DB() as db:
        uid = await db.next_uid('dynamic')
        if not uid:
            return
        push_list = await db.get_push_list(uid, 'dynamic')
        push_list = [{'bot_id': target.bot_id,
                      'type': target.type,
                      'type_id': target.type_id} for target in push_list]
        name = (await db.get_user(uid)).name

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
            try:
                # TODO 怎么好像一截图就会卡死的样子
                await dynamic.get_screenshot()
            except AttributeError:
                return
            await dynamic.format()

            for sets in push_list:
                await safe_send(sets['bot_id'], sets['type'], sets['type_id'], dynamic.message)
            last_time[uid] = dynamic.time
