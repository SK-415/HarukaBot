import nonebot
import os
from nonebot import scheduler
from .utils import Dynamic, User
from .utils import read_config
from datetime import datetime, timedelta
from nonebot.log import logger


last_time = {}
index = 0

@scheduler.scheduled_job('cron', second='*/10', id='dynamic_sched')
@logger.catch
async def dy_sched():
    config = await read_config()
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
    dynamics = (await user.get_dynamic())['cards'] # 获取最近十二条动态
    # config['uid'][uid]['name'] = dynamics[0]['desc']['user_profile']['info']['uname']
    # await update_config(config)

    if uid not in last_time:
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
            bots = nonebot.get_bots()
            for group_id, bot_id in config["uid"][uid]["groups"].items():
                if config["groups"][group_id]['uid'][uid]["dynamic"]:
                    bot = bots[bot_id]
                    await bot.send_group_msg(group_id=group_id, message=dynamic.message)
            for user_id, bot_id in config["uid"][uid]["users"].items():
                if config["users"][user_id]['uid'][uid]["dynamic"]:
                    bot = bots[bot_id]
                    await bot.send_private_msg(user_id=user_id, message= dynamic.message)
            last_time[uid] = dynamic.time