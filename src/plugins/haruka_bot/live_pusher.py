import nonebot
from apscheduler.triggers.cron import CronTrigger
from nonebot import scheduler
from nonebot.log import logger

from .utils import BiliAPI, safe_send
from .config import Config

uids = {}

@scheduler.scheduled_job('cron', second='*/10', id='live_sched')
@logger.catch
async def live_sched():
    """直播推送"""

    with Config() as config:
        uid = config.next_uid('live')
        if not uid:
            return
        if uid not in uids:
            uids[uid] = 1
        push_list = config.get_push_list(uid, 'live')
        
    old_status = uids[uid]
    api = BiliAPI()
    user_info = (await api.get_info(uid))['live_room']
    name = push_list[0]['name']
    logger.debug(f'爬取直播 {name}（{uid}）')
    new_status = user_info['liveStatus']
    if new_status == old_status:
        return

    uids[uid] = new_status
    if new_status:
        live_msg = f"{name} 开播啦！\n\n{user_info['title']}\n传送门→{user_info['url']}\n[CQ:image,file={user_info['cover']}]"
        for sets in push_list:
            at_msg = ''
            if sets['at']:
                at_msg = '[CQ:at,qq=all] '
            bot = nonebot.get_bots()[sets['bot_id']]
            await safe_send(bot, sets['type'], sets['type_id'], at_msg + live_msg)
