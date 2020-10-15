import nonebot
from nonebot import scheduler
from .utils import read_config, update_config
from .utils import User
from nonebot.log import logger


@scheduler.scheduled_job('cron', second='*/10', id='live_sched')
@logger.catch
async def _():
    config = await read_config()
    ups = config['status']
    
    uid_list = config['live']['uid_list']
    if not uid_list:
        return
    if config['live']['index'] >= len(uid_list):
        uid = uid_list[0]
        config['live']['index'] = 1
    else:
        uid = uid_list[config['live']['index']]
        config['live']['index'] += 1
    await update_config(config)

    old_status = ups[uid]
    user = User(uid)
    user_info = (await user.get_info())['live_room']
    new_status = user_info['liveStatus']
    if new_status != old_status:
        config['status'][uid] = new_status
        await update_config(config)

        if new_status:
            bots = nonebot.get_bots()
            name = (await user.get_info())['name'] # 获取昵称应转移至配置文件
            live_msg = f"{name} 开播啦！\n\n{user_info['title']}\n传送门→{user_info['url']}\n[CQ:image,file={user_info['cover']}]"
            groups = config["uid"][uid]["groups"]
            for group_id, bot_id in groups.items():
                if config["groups"][group_id]['uid'][uid]["live_reminder"]:
                    bot = bots[bot_id]
                    if config['groups'][group_id]['uid'][uid]['at']:
                        await bot.send_group_msg(group_id=group_id, message="[CQ:at,qq=all] "+live_msg)
                    else:
                        await bot.send_group_msg(group_id=group_id, message=live_msg)
            users = config["uid"][uid]["users"]
            for user_id, bot_id in users.items():
                if config["users"][user_id]['uid'][uid]["live_reminder"]:
                    bot = bots[bot_id]
                    await bot.send_private_msg(user_id=user_id, message=live_msg)
