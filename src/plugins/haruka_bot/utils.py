import asyncio
import base64
import json
import os
import traceback
from datetime import datetime
from os import path

import httpx
import aiofiles
import nonebot
from nonebot.adapters.cqhttp import Bot
from nonebot.log import logger
from nonebot import get_driver

os.environ['PYPPETEER_DOWNLOAD_HOST'] = 'http://npm.taobao.org/mirrors'
# os.environ['PYPPETEER_DOWNLOAD_HOST'] = 'http://storage.googleapis.com'
from pyppeteer import launch
from pyppeteer.chromium_downloader import check_chromium, download_chromium

if not check_chromium():
    download_chromium()

class Dynamic():
    def __init__(self, dynamic):
        # self.origin = json.loads(self.card['origin'])
        self.dynamic = dynamic
        # self.card = json.loads(dynamic['card'])
        # self.dynamic['card'] = self.card
        self.type = dynamic['desc']['type']
        self.id = dynamic['desc']['dynamic_id']
        self.url = "https://t.bilibili.com/" + str(self.id)
        self.time = dynamic['desc']['timestamp']
        # self.origin_id = dynamic['desc']['orig_dy_id']
        self.name = dynamic['desc']['user_profile']['info']['uname']
        self.uid = dynamic['desc']['user_profile']['info']['uid']
        self.img_name = str(self.uid) + str(self.time) + '.png'
        self.img_path = get_path(self.img_name)

    async def format(self):
        if self.type == 1:
            self.message = f"{self.name}转发了一条动态：\n\n传送门→" + self.url + "[CQ:image,file=" + self.image + "]\n"
            return self.message
        elif self.type == 8:
            bv_url = 'https://www.bilibili.com/video/' + self.dynamic['desc']['bvid']
            self.message = f"{self.name}发布了新投稿\n\n传送门→" + bv_url + "[CQ:image,file=" + self.image + "]\n"
        elif self.type == 16:
            self.message = f"{self.name}发布了短视频\n\n传送门→" + self.url + "[CQ:image,file=" + self.image + "]\n"
        elif self.type == 64:
            self.message = f"{self.name}发布了新专栏\n\n传送门→" + self.url + "[CQ:image,file=" + self.image + "]\n"
        elif self.type == 256:
            self.message = f"{self.name}发布了新音频\n\n传送门→" + self.url + "[CQ:image,file=" + self.image + "]\n"
        else:
            self.message = f"{self.name}发布了新动态\n\n传送门→" + self.url + "[CQ:image,file=" + self.image + "]\n"

    async def get_screenshot(self):
        if path.isfile(self.img_path):
            return
        browser = await launch(args=['--no-sandbox'])
        page = await browser.newPage()
        for _ in range(3):
            try:
                await page.goto(self.url, waitUntil="networkidle0")
                # await page.waitForNavigation()
                # await page.waitFor(1000)
                await page.setViewport(viewport={'width': 1920, 'height': 1080})
                # card = await page.waitForSelector(".card")
                card = await page.querySelector(".card")
                clip = await card.boundingBox()
                bar = await page.querySelector(".text-bar")
                bar_bound = await bar.boundingBox()
                clip['height'] = bar_bound['y'] - clip['y']
                await page.screenshot({'path': self.img_path, 'clip': clip})
                break
            except:
                logger.error(traceback.format_exc())
                await asyncio.sleep(0.1)
        await page.close()
        await browser.close()
    
    async def encode(self):
        """将图片转为base64码"""
        with open(self.img_path, 'rb') as f:
            self.image = "base64://" + base64.b64encode(f.read()).decode('utf-8')
            return self.image
    
    async def get_path(self):
        self.image = "file:///" + self.img_path
        return self.image


class Config():
    """操作 config.json 文件"""

    def __init__(self, event=None):
        self.config = None
        if event:
            self.id = event.self_id
            if event.detail_type == 'private':
                self.type = 'users'
                self.type_id = str(event.user_id)
            else:
                self.type = 'groups'
                self.type_id = str(event.group_id)
    
    async def read(self):
        """读取用户注册信息"""

        try:
            async with aiofiles.open(get_path('config.json'), encoding='utf-8-sig') as f:
                text = await f.read()
            self.config = json.loads(text)
        except FileNotFoundError:
            self.config = self.new()
        return self.config

    def new(self):
        """生成新的配置文件"""

        self.config = {
            "status": {},
            "uid": {},
            "groups": {},
            "users": {},
            "dynamic": {
                "uid_list": []
            },
            'live': {
                'uid_list': []
            }
        }
        return self.config
    
    async def update(self, config):
        """更新注册信息"""
        
        # await self.read()
        async with aiofiles.open(get_path('config.json'), 'w', encoding='utf-8') as f:
            await f.write(json.dumps(config, ensure_ascii=False, indent=4))
    
    async def add_uid(self, uid):
        """添加主播"""

        await self.read()
        if uid not in self.config["status"]: # uid不在配置文件就创建一个
            user = User(uid)
            name = ''
            try: # 应该改uid有效检测逻辑
                user_info = await user.get_info()
                name = user_info["name"]
            except:
                return("请输入有效的uid")
            self.config['status'][uid] = 0
            self.config['uid'][uid] = {'groups': {}, 'users': {}, 'dynamic': 0, 'live': 0, 'name': name}
            self.config['dynamic']['uid_list'].append(uid) # 主播uid添加至动态列表
            self.config['live']['uid_list'].append(uid) # 主播uid添加至直播列表
        else:
            name = self.config['uid'][uid]['name']
            if uid not in self.config['dynamic']['uid_list']: 
                self.config['dynamic']['uid_list'].append(uid)
            if uid not in self.config['live']['uid_list']:
                self.config['live']['uid_list'].append(uid)

        if self.type_id not in self.config['uid'][uid][self.type]:
            self.config['uid'][uid][self.type][self.type_id] = self.id
        else:
            return f'请勿重复添加 {name}（{uid}）'
        if self.type_id in self.config[self.type]:
            self.config[self.type][self.type_id]['uid'][uid] = {'live': True, 'dynamic': True}
        else:
            self.config[self.type][self.type_id] = {'uid': {uid: {'live': True, 'dynamic': True}}}
        if self.type == 'groups':
            self.config[self.type][self.type_id]['uid'][uid]['at'] = False
            if 'admin' not in self.config[self.type][self.type_id]:
                self.config[self.type][self.type_id]['admin'] = True

        self.config['uid'][uid]['dynamic'] += 1
        self.config['uid'][uid]['live'] += 1
        await self.update(self.config)
        return f"已添加 {name}（{uid}）"
    
    async def delete_uid(self, uid):
        """删除主播"""

        await self.read()
        try:
            name = self.config['uid'][uid]['name']
            if self.config[self.type][self.type_id]['uid'][uid]['dynamic']:
                self.config['uid'][uid]['dynamic'] -= 1
            if self.config[self.type][self.type_id]['uid'][uid]['live']:
                self.config['uid'][uid]['live'] -= 1
            del self.config[self.type][self.type_id]['uid'][uid]
            del self.config['uid'][uid][self.type][self.type_id]
            # 如果用户没有关注则删除用户
            if self.config[self.type][self.type_id]['uid'] == {} and (
                'admin' not in self.config[self.type][self.type_id]['uid'] or
                self.config[self.type][self.type_id]['admin']):
                del self.config[self.type][self.type_id]
        except KeyError:
            return "删除失败，uid 不存在"

        # 如果无人再订阅动态，就从动态列表中移除
        if self.config['uid'][uid]['dynamic'] == 0 and uid in self.config['dynamic']['uid_list']:
            self.config['dynamic']['uid_list'].remove(uid)
        # 如果无人再订阅直播，就从直播列表中移除
        if self.config['uid'][uid]['live'] == 0 and uid in self.config['live']['uid_list']:
            self.config['live']['uid_list'].remove(uid)
        # 如果没人订阅该主播，则将该主播彻底删除
        if self.config['uid'][uid]['groups'] == {} and self.config['uid'][uid]['users'] == {}:
            del self.config['uid'][uid]
            del self.config['status'][uid]
        
        await self.update(self.config)
        return f"已删除 {name}（{uid}）"

    async def uid_list(self):
        await self.read()
        try:
            uid_list = self.config[self.type][self.type_id]['uid']
        except KeyError:
            uid_list = {}
        message = "以下为当前的订阅列表：\n\n"
        for uid, status in uid_list.items():
            name = self.config['uid'][uid]['name']
            message += f"【{name}】"
            message += f"直播推送：{'开' if status['live'] else '关'}，"
            message += f"动态推送：{'开' if status['dynamic'] else '关'}"
            message += f"（{uid}）\n"
        return message

    async def set(self, func, uid, status):
        """开关各项功能"""

        if func == 'at' and self.type == 'users':
            return "只有群里才能name"

        await self.read()
        try:
            name = self.config['uid'][uid]['name']
            if self.config[self.type][self.type_id]['uid'][uid][func] == status:
                return "请勿重复name"
            self.config[self.type][self.type_id]['uid'][uid][func] = status

            if func not in self.config['uid'][uid]:
                await self.update(self.config)
                return f"已name，{name}（{uid}）"

            if status:
                self.config['uid'][uid][func] += 1
                # 如果是第一个开启的，就添加至爬取列表
                if self.config['uid'][uid][func] == 1:
                    self.config[func]['uid_list'].append(uid)
            else:
                self.config['uid'][uid][func] -= 1
                # 如果无人再订阅动态，就从爬取列表中移除
                if self.config['uid'][uid][func] == 0:
                    self.config[func]['uid_list'].remove(uid)
        except KeyError:
            return "name失败，uid 不存在"

        await self.update(self.config)
        return f"已name，{name}（{uid}）"

    async def set_permission(self, status):
        if self.type == 'users':
            return "只有群里才能name"
        
        await self.read()
        if self.type_id not in self.config['groups']:
            if status:
                return "请勿重复name"
            else:
                self.config['groups'][self.type_id] = {'uid': {}, 'admin': False}
        elif self.config['groups'][self.type_id]['admin'] == status:
            return "请勿重复name"
        else:
            self.config['groups'][self.type_id]['admin'] = status

        await self.update(self.config)
        message = "已name，只有管理员才能使用" if status else "已name，所有人都能使用"
        return message

    # async def next_uid(self, func):
    #     uid_list = config['live']['uid_list']
    #     global index
    #     if not uid_list:
    #         return
    #     if index >= len(uid_list):
    #         uid = uid_list[0]
    #         index = 1
    #     else:
    #         uid = uid_list[index]
    #         index += 1

    async def backup(self):
        """备份当前配置文件"""

        await self.read()
        backup_name = f"config.{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json.bak"
        async with aiofiles.open(get_path(backup_name), 'w', encoding='utf-8') as f:
            await f.write(json.dumps(self.config, ensure_ascii=False, indent=4))
        return True


class User():
    def __init__(self, uid):
        self.uid = str(uid)
    
    async def get_info(self):
        url = f'https://api.bilibili.com/x/space/acc/info?mid={self.uid}'
        return (await Get(url))['data']

    async def get_dynamic(self):
        # need_top: {1: 带置顶, 0: 不带置顶}
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={self.uid}&offset_dynamic_id=0&need_top=0'
        return (await Get(url))['data']
    
    async def get_live_info(self):
        url = f'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={self.uid}'
        return (await Get(url))['data']


async def Get(url):
    DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/79.0.3945.130 Safari/537.36",
    "Referer": "https://www.bilibili.com/"
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=DEFAULT_HEADERS)
    r.encoding = 'utf-8'
    return r.json()


def get_path(name):
    """获取数据文件绝对路径"""
    config = get_driver().config
    if config.haruka_dir:
        dir_path = path.abspath(config.haruka_dir)
    else:
        src_path = path.dirname(path.abspath(__file__))
        dir_path = path.join(src_path, 'data')
    f_path = path.join(dir_path, name)
    return f_path


async def safe_send(bot: Bot, send_type, type_id, message):
    """发送出现错误时, 尝试重新发送, 并捕获异常且不会中断运行"""
    for i in range(3):
        try:
            message_id = await bot.call_api('send_'+send_type+'_msg', **{
                'message': message,
                'user_id' if send_type == 'private' else 'group_id': type_id
                })
            return message_id
        except:
            logger.error(traceback.format_exc())
            if i == 2:
                bot = await restart(bot)
                warning_msg = '检测到推送出现异常，已尝试自动重启，如仍有问题请向机器人管理员反馈'
                await bot.call_api('send_'+send_type+'_msg', **{
                    'message': warning_msg,
                    'user_id' if send_type == 'private' else 'group_id': type_id
                    })
                message_id = await bot.call_api('send_'+send_type+'_msg', **{
                'message': message,
                'user_id' if send_type == 'private' else 'group_id': type_id
                })
                return message_id
            await asyncio.sleep(0.1)


async def restart(bot: Bot):
    await bot.set_restart()
    await asyncio.sleep(1)
    while True:
        new_bot = nonebot.get_bots().get(bot.self_id, None)
        if new_bot:
            break
        await asyncio.sleep(0.1)
    return new_bot


# bot 启动时检查 src\data\haruka_bot\ 目录是否存在
if not path.isdir(get_path('')):
    os.makedirs(get_path(''))
