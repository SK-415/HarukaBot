from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.log import logger

from ...database import DB
from ...libs.bilireq import BiliReq
from ...utils import safe_send, scheduler

status = {}

@scheduler.scheduled_job('interval', seconds=10, id='live_sched')
async def live_sched():
    """直播推送"""

    async with DB() as db:
        uids = await db.get_uid_list('live')

    if not uids:
        return
    logger.debug(f'爬取直播列表，目前开播{sum(status.values())}人，总共{len(uids)}人')
    br = BiliReq()
    res = await br.get_live_list(uids)
    if not res:
        return
    for uid, info in res.items():
        new_status = 0 if info['live_status'] == 2 else info['live_status']
        if uid not in status:
            status[uid] = new_status
            continue
        old_status = status[uid]
        if new_status != old_status and new_status: # 判断是否推送过
            room_id = info['short_id'] if info['short_id'] else info['room_id']
            url = 'https://live.bilibili.com/' + str(room_id)
            name = info['uname']
            title = info['title']
            cover = (info['cover_from_user'] if info['cover_from_user']
                                             else info['keyframe'])
            logger.info(f"检测到开播：{name}（{uid}）")

            live_msg = (f"{name} 正在直播：\n{title}\n" + 
                        MessageSegment.image(cover) + f"\n{url}")
            async with DB() as db:
                push_list = await db.get_push_list(uid, 'live')
                for sets in push_list:
                    await safe_send(
                        bot_id = sets.bot_id,
                        send_type = sets.type,
                        type_id = sets.type_id,
                        message = live_msg,
                        at = sets.at
                    )
                await db.update_user(uid, name)
        status[uid] = new_status
