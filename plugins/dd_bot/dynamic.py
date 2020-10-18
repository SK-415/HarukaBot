import nonebot
import os
from nonebot import scheduler
from .utils import Dynamic, Dydb, User
from .utils import read_config, update_config
from datetime import datetime, timedelta
from nonebot.log import logger


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

    print('动态:', index, uid)
    user = User(uid)
    dynamics = (await user.get_dynamic())['cards'] # 获取最近十二条动态
    # config['uid'][uid]['name'] = dynamics[0]['desc']['user_profile']['info']['uname']
    # await update_config(config)

    dydb = Dydb()
    data = dydb.run_command(f'select * from uid{uid} order by time desc limit 3 offset 0')
    if not data:
        for dynamic in dynamics: # 添加最近十二条动态进数据库
            dynamic = Dynamic(dynamic)
            dydb.insert_uid(uid, dynamic.time, dynamic.url, True)
        return

    last_time = data[0][0]
    for dynamic in reversed(dynamics[:3]): # 取最近3条动态
        dynamic = Dynamic(dynamic)
        if dynamic.time > last_time and dynamic.time > datetime.now().timestamp() - timedelta(minutes=10).seconds:
            await dynamic.get_screenshot()
            await dynamic.encode()
            os.remove(dynamic.img_path)
            await dynamic.format()
            bots = nonebot.get_bots()
            for group_id, bot_id in config["uid"][uid]["groups"].items():
                if config["groups"][group_id]['uid'][uid]["dynamic"]:
                    bot = bots[bot_id]
                    message_id = (await bot.send_group_msg(group_id=group_id, message=dynamic.message))['message_id']
                    dydb.insert_qq(group_id, dynamic.url, message_id, bot_id)
            for user_id, bot_id in config["uid"][uid]["users"].items():
                if config["users"][user_id]['uid'][uid]["dynamic"]:
                    bot = bots[bot_id]
                    await bot.send_private_msg(user_id=user_id, message= dynamic.message)
            dydb.insert_uid(dynamic.uid, dynamic.time, dynamic.url, False)
