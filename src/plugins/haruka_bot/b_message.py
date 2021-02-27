from nonebot.log import logger
from .utils import scheduler
import asyncio,json,httpx
from .config import Config
import random,uuid,time,datetime

def getcode(data):
    seeds = "0123456789"
    random_str = random.sample(seeds, data)
    code_ =("".join(random_str))
    code = {
        "code":code_
    }
    return code
async def send_msg(self,uid,pig):
    '私信'
    url = "https://api.vc.bilibili.com/web_im/v1/web_im/send_msg"
    with Config() as config:
        cookie = config.get_login()
        codes = getcode(4)['code']
        receiver_id = uid
        title = "NGWORKS"
        msg = "【" + title + "】验证码："+ str(codes) + "，用于验证你的账号,请勿泄露，5分钟有效，非本人操作请勿回复。"
        jmsg = {
            'content':msg
            }
        t = int(time.time()*1000)
        x=str(uuid.uuid4())
        datas = {
            'msg[sender_uid]':cookie['DedeUserID'],
            'msg[receiver_id]':receiver_id,
            'msg[receiver_type]':1,
            'msg[msg_type]':1,
            'msg[msg_status]': 0,
            'msg[content]':json.dumps(jmsg),
            'csrf_token':cookie['bili_jct'],
            'csrf':cookie['bili_jct'],
            'msg[timestamp]': t,
            'msg[dev_id]': x,
            'build': 0,
            'mobi_app': 'web'
        }
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params = datas, cookies = cookie)
            rep_json = r.json()
            print(rep_json)
            return rep_json