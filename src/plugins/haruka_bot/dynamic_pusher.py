from datetime import datetime, timedelta

from nonebot.log import logger

from .bilireq import BiliReq
from .config import Config
from .dynamic import Dynamic
from .utils import safe_send, scheduler

last_time = {}

@scheduler.scheduled_job('cron', second='*/10', id='dynamic_sched')
async def dy_sched():
    """动态推送"""

    with Config() as config:
        uid = config.next_uid('dynamic')
        if not uid:
            return
        push_list = config.get_push_list(uid, 'dynamic')
    
    name = push_list[0]['name']
    logger.debug(f'爬取动态 {name}（{uid}）')
    b = BiliReq()
    dynamics = (await b.get_user_dynamics(uid)).get('cards', []) # 获取最近十二条动态
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
                await dynamic.get_screenshot()
            except AttributeError:
                return
            await dynamic.format()

            for sets in push_list:
                # 发之前截下先看看
                # 先搞过来看看type是不是group
                if sets['type'] == "group":
                    try:
                    # 旧数据没有dynamic_at，为了防止报错
                        if sets['dynamic_at']:
                            # 开启@全员
                            mess = f"[CQ:at,qq=all]" + dynamic.message
                        else:
                            # 没开@全员
                            mess = dynamic.message
                    except:
                        mess = dynamic.message
                else:
                    # 私聊推送
                    mess = dynamic.message

                await safe_send(sets['bot_id'], sets['type'], sets['type_id'], mess)
            last_time[uid] = dynamic.time
