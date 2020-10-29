import nonebot
from nonebot import scheduler
from nonebot.log import logger

from .utils import User, read_config, safe_send, update_config

index = 0

@scheduler.scheduled_job('cron', second='*/10', id='live_sched')
@logger.catch
async def live_sched():
    config = await read_config()
    ups = config['status']
    
    uid_list = config['live']['uid_list']
    global index
    if not uid_list:
        return
    if index >= len(uid_list):
        uid = uid_list[0]
        index = 1
    else:
        uid = uid_list[index]
        index += 1

    old_status = ups[uid]
    user = User(uid)
    user_info = (await user.get_info())['live_room']
    name = config['uid'][uid]['name'] # 直接从配置文件读取名字
    logger.debug(f'爬取直播 [{index:03}] {name}({uid})')
    new_status = user_info['liveStatus']
    if new_status != old_status:
        config = await read_config()
        config['status'][uid] = new_status
        await update_config(config)

        if new_status:
            bots = nonebot.get_bots()
            # name = (await user.get_info())['name'] # 获取昵称应转移至配置文件
            live_msg = f"{name} 开播啦！\n\n{user_info['title']}\n传送门→{user_info['url']}\n[CQ:image,file={user_info['cover']}]"
            groups = config["uid"][uid]["groups"]
            for group_id, bot_id in groups.items():
                if config["groups"][group_id]['uid'][uid]["live"]:
                    bot = bots[bot_id]
                    if config['groups'][group_id]['uid'][uid]['at']:
                        await safe_send(bot, 'group', group_id, "[CQ:at,qq=all] "+live_msg)
                    else:
                        await safe_send(bot, 'group', group_id, live_msg)
            users = config["uid"][uid]["users"]
            for user_id, bot_id in users.items():
                if config["users"][user_id]['uid'][uid]["live"]:
                    bot = bots[bot_id]
                    await safe_send(bot, 'private', user_id, live_msg)
