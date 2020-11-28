import os
from datetime import datetime, timedelta

import nonebot
from nonebot import scheduler
from nonebot.log import logger

from .utils import Dynamic, User, Config, safe_send

last_time = {}
index = 0

@scheduler.scheduled_job('cron', second='*/10', id='dynamic_sched')
@logger.catch
async def dy_sched():
    c = Config()
    config = await c.read()
    ups = config['dynamic']['uid_list']

    uid_list = ups
    global index
    if not uid_list:
        return
    if index >= len(uid_list):
        uid = uid_list[0]
        index = 1
    else:
        uid = uid_list[index]
        index += 1

    name = config['uid'][uid]['name'] # 直接从配置文件读取名字
    logger.debug(f'爬取动态 [{index:03}] {name}({uid})')
    user = User(uid)
    dynamics = (await user.get_dynamic()).get('cards', []) # 获取最近十二条动态
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
            await dynamic.get_screenshot()
            await dynamic.encode()
            os.remove(dynamic.img_path)
            await dynamic.format()
            for group_id, bot_id in config["uid"][uid]["groups"].items():
                if config["groups"][group_id]['uid'][uid]["dynamic"]:
                    bots = nonebot.get_bots()
                    bot = bots[bot_id]
                    await safe_send(bot, 'group', group_id, dynamic.message)
            for user_id, bot_id in config["uid"][uid]["users"].items():
                if config["users"][user_id]['uid'][uid]["dynamic"]:
                    bots = nonebot.get_bots()
                    bot = bots[bot_id]
                    await safe_send(bot, 'private', user_id, dynamic.message)
            last_time[uid] = dynamic.time
