import nonebot
from nonebot.log import logger

from .config import Config
from .utils import safe_send, scheduler
from .bilireq import BiliReq


status = {}

@scheduler.scheduled_job('cron', second='*/10', id='live_sched')
@logger.catch
async def live_sched():
    """直播推送"""

    with Config() as config:
        uids = config.get_uid_list('live')
        if not uids:
            return
        br = BiliReq()
        logger.debug(f'爬取直播列表')
        r = await br.get_live_list(uids)
        for uid, info in r.items():
            if uid not in status:
                status[uid] = 1
            old_status = status[uid]
            new_status = 0 if info['live_status'] == 2 else info['live_status']
            if new_status == old_status:
                return
            status[uid] = new_status
            if new_status:
                room_id = info['short_id'] if info['short_id'] else info['room_id']
                url = 'https://live.bilibili.com/' + str(room_id)
                name = info['uname']
                title = info['title']
                cover = info['cover_from_user'] if info['cover_from_user'] else info['keyframe']
                push_list = config.get_push_list(uid, 'live')

                live_msg = f"{name} 开播啦！\n\n{title}\n传送门→{url}\n[CQ:image,file={cover}]"
                for sets in push_list:
                    at_msg = '[CQ:at,qq=all] ' if sets['at'] else ''
                    bot = nonebot.get_bots()[sets['bot_id']]
                    await safe_send(bot, sets['type'], sets['type_id'], at_msg + live_msg)
