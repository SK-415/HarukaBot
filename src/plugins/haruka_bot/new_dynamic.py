from nonebot import require
from nonebot.log import logger
from .utils import scheduler
import asyncio,json,httpx
from .config import Config
from .login_manage import BiliApi
from .mod import RedisDB
from .dynamic import Dynamic
from .utils import safe_send, scheduler
@scheduler.scheduled_job('cron', second='*/5', id='new_dynamic')
async def new_dynamic():
    "获取新动态的操作"
    time = 60000000000
    with RedisDB(11)as db:
        base_dynamic_id = db.get('dynamic_id') 
        base_timestamp = db.get('timestamp') 
        if base_dynamic_id == None or base_timestamp == None:
            dt = await BiliApi().dynamic_new(123456789)
            base_dynamic_id = dt['max_dynamic_id']
            base_timestamp = dt['data'][0]['timestamp']
            db.set('dynamic_id',dt['max_dynamic_id'],time)
            db.set('timestamp',dt['data'][0]['timestamp'],time)
            logger.debug(f"找不到dynamic_id,初始dynamic_id将会重置。")
        data = await BiliApi().dynamic_new(base_dynamic_id)
        if data['count'] == 0:
            logger.info(f"爬取动态 目前没有新动态哦！")
        elif data['count'] == 20:
            newlist = []
            for dy in data['data']:
                newlist.append(dy)
            logger.debug(f"爬取动态 列表等于20，将进行回滚判断")
            listlastid = data['data'][19]['dynamic_id']
            # 开始找根id，找到为止，要是被删除就判断时间戳
            while True:
                dt = False
                history_data = await BiliApi().dynamic_history(listlastid)
                for dycards in history_data['data']:
                    ids = dycards['dynamic_id']
                    timestamp = dycards['timestamp']
                    if ids == base_dynamic_id or timestamp < int(base_timestamp):
                        dt = True
                        break
                    newlist.append(dycards)
                count = len(history_data['data'])
                listlastid = history_data['data'][count-1]['dynamic_id']
                if dt:
                    break
            logger.debug(f"爬取列表成功")
            db.set('dynamic_id',data['max_dynamic_id'],time)
            db.set('timestamp',data['data'][0]['timestamp'],time)
        else:
            logger.info(f"爬取动态 账号列表模式！")
            newlist = []
            for dy in data['data']:
                newlist.append(dy)
            logger.debug(f"爬取列表成功")
            db.set('dynamic_id',data['max_dynamic_id'],time)
            db.set('timestamp',data['data'][0]['timestamp'],time)
    try:
        for pr in newlist:
            logger.debug(f"{pr['uname']}{pr['type_message']}=>{pr['message']}")
        with Config() as config:
            group = await config.group_uid_list()
            for key,value in group.items():
                group = key
                userlist = value
                uidlist = []
                userdict = {}
                for userd in value:
                    uid = int(userd['uid'])
                    uidlist.append(uid)
                    userdict[uid] = {"type":userd['type'],"type_id":userd['type_id'],"dynamic":userd['dynamic'],"at":userd['at'],"bot_id":userd["bot_id"],"dynamic_at":userd['dynamic_at']}
                for dynamic_list in newlist:
                    if (int(dynamic_list['uid']) in uidlist):
                        sets = userdict[int(dynamic_list['uid'])]
                        if sets['type'] == "group" and sets['dynamic']:
                            message = f"{dynamic_list['uname']}{dynamic_list['type_message']}：" +\
                            f"\n\n内容是：{dynamic_list['message']}\n"
                            await safe_send(sets['bot_id'], sets['type'], sets['type_id'], message)
    except:
        pass

