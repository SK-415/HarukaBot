import asyncio
import base64
import json
import os
import traceback
from datetime import datetime
from os import path

import httpx
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


async def read_config():
    """读取用户注册信息"""
    try:
        with open(get_path('config.json'), encoding='utf-8-sig') as f:
            config = json.loads(f.read())
    except FileNotFoundError:
        config = get_new_config()
    return config


def get_new_config():
    return {"status": {}, "uid": {}, "groups": {}, "users": {}, "dynamic": {"uid_list": []}, 'live': {'uid_list': []}}


async def update_config(config):
    """更新注册信息"""
    with open(get_path('config.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(config, ensure_ascii=False, indent=4))


async def backup_config(config):
    # backup_name = f"config{datetime.now().strftime('%Y.%m.%d %H-%M-%S')}.json"
    backup_name = f"config{int(datetime.now().timestamp())}.json"
    with open(get_path(backup_name), 'w', encoding='utf-8') as f:
        f.write(json.dumps(config, ensure_ascii=False, indent=4))


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
