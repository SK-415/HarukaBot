from nonebot import on_request
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp.permission import PRIVATE_FRIEND
from .mod import RedisDB
from .bilireq import BiliReq



friend_req = on_request(priority=5)

@friend_req.handle()
async def _(bot: Bot, event: Event, state: dict):
    if event.request_type == 'friend' and str(event.user_id) in bot.config.superusers:
        await bot.set_friend_add_request(flag=event.flag, approve=True)


group_invite = on_request(priority=5)

@group_invite.handle()
async def _(bot: Bot, event: Event, state: dict):
    if event.request_type == 'group' and event.sub_type == 'add':
        # 收到加群请求
        print(event)
        qq = event.user_id
        msg = event.comment
        str2 = f'\n答案：'
        s = msg[ msg.index(str2)+4:]
        print(s)
        b = BiliReq() 
        with RedisDB(11) as db:
            try:
                # 查库看看这个qq有没有匹配过uid
                uid =  db.get(qq)
                code = db.get(uid)
                msg = await b.codetest(qq,code)
                # 判断
                if msg == "验证通过":
                    await bot.set_group_add_request(flag=event.flag, sub_type='add', approve=True)
                else:
                    await bot.set_group_add_request(flag=event.flag, reason=str(msg), sub_type='add', approve=False)
            except:
                #没有的话抛到这边新申请
                try:
                    uid = int(s)
                    res = await b.get_info(uid=uid)
                    # if res['code'] != 0:
                    #     raise ValueError('错误的uid')
                    # uname = res['data']['name']
                    dt = await b.send_msg(uid=uid,qq=int(qq))
                    await bot.set_group_add_request(flag=event.flag, reason="看B站私信，根据指引完成后续操作0。", sub_type='add', approve=False)
                except Exception as e:
                
                    await bot.set_group_add_request(flag=event.flag, reason=str(e), sub_type='add', approve=False)


            
        # await bot.set_group_add_request(flag=event.flag, sub_type='add', approve=True)