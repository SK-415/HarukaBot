from bilireq.live import get_rooms_info_by_uids
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.log import logger

from ... import config
from ...database import DB as db
from ...utils import PROXIES, safe_send, scheduler

status = {}


@scheduler.scheduled_job(
    "interval", seconds=config.haruka_live_interval, id="live_sched"
)
async def live_sched():
    """直播推送"""
    uids = await db.get_uid_list("live")

    if not uids:  # 订阅为空
        return
    logger.debug(f"爬取直播列表，目前开播{sum(status.values())}人，总共{len(uids)}人")
    res = await get_rooms_info_by_uids(uids, reqtype="web", proxies=PROXIES)
    if not res:
        return
    for uid, info in res.items():
        new_status = 0 if info["live_status"] == 2 else info["live_status"]
        if uid not in status:
            status[uid] = new_status
            continue
        old_status = status[uid]
        if new_status == old_status:  # 直播间状态无变化
            continue
        status[uid] = new_status

        name = info["uname"]
        if new_status:  # 开播
            room_id = info["short_id"] if info["short_id"] else info["room_id"]
            url = "https://live.bilibili.com/" + str(room_id)
            title = info["title"]
            cover = (
                info["cover_from_user"] if info["cover_from_user"] else info["keyframe"]
            )
            logger.info(f"检测到开播：{name}（{uid}）")

            live_msg = (
                f"{name} 正在直播：\n{title}\n" + MessageSegment.image(cover) + f"\n{url}"
            )
        else:  # 下播
            logger.info(f"检测到下播：{name}（{uid}）")
            if not config.haruka_live_off_notify:  # 没开下播推送
                continue
            live_msg = f"{name} 下播了"

        # 推送
        push_list = await db.get_push_list(uid, "live")
        for sets in push_list:
            await safe_send(
                bot_id=sets.bot_id,
                send_type=sets.type,
                type_id=sets.type_id,
                message=live_msg,
                at=bool(sets.at) if new_status else False,  # 下播不@全体
            )
        await db.update_user(int(uid), name)
