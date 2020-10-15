import sqlite3
import requests
import json
import base64
from pyppeteer import launch
# import asyncio
# import os
# import sys
from os import path
# import functools
# from nonebot.log import logger
# import traceback
import aiohttp


class Dydb():
    def __init__(self):
        self.path = get_path('dynamic.db')

    def run_command(self, command, variables=[]):
        conn = sqlite3.connect(self.path)
        cursor = conn.cursor()
        cursor.execute(command, variables)
        results = cursor.fetchall()
        cursor.close()
        conn.commit()
        conn.close()
        return results

    def get_table_list(self):
        command = 'select name from sqlite_master where type="table" order by name;'
        tables = self.run_command(command)
        return [table[0] for table in tables]

    def create_table(self, name, table_frame):
        command = f'create table {name} {table_frame}'
        self.run_command(command)

    def insert_uid(self, uid, time, url, is_recall):
        command = f'insert into uid{uid} (time, url, is_recall) values (?, ?, ?)'
        self.run_command(command, (time, url, is_recall))
    
    def insert_qq(self, group_id, url, message_id, bot_id):
        command = f'insert into qq{group_id} (url, message_id, bot_id) values (?, ?, ?)'
        self.run_command(command, (url, message_id, bot_id))


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
        await page.goto(self.url, waitUntil="networkidle0")
        # await page.waitForNavigation()
        # await page.waitFor(1000)
        await page.setViewport(viewport={'width': 1920, 'height': 1080})
        card = await page.waitForSelector(".card")
        # card = await page.querySelector(".card")
        clip = await card.boundingBox()
        bar = await page.querySelector(".text-bar")
        bar_bound = await bar.boundingBox()
        clip['height'] = bar_bound['y'] - clip['y']
        await page.screenshot({'path': self.img_path, 'clip': clip})
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

    async def test_img(self):
        return f"哈哈[CQ:image,file=" + self.image + "]"

class User():
    def __init__(self, uid):
        self.uid = str(uid)
    
    async def get_info(self):
        url = f'https://api.bilibili.com/x/space/acc/info?mid={self.uid}'
        return (await Get(url))['data']

    async def get_dynamic(self):
        # need_top: {1: 带置顶, 2: 不带置顶}
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={self.uid}&offset_dynamic_id=0&need_top=0'
        return (await Get(url))['data']
    
    async def get_live_info(self):
        url = f'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={self.uid}'
        return (await Get(url))['data']


async def Get(url):
    # start = time.time()
    DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/79.0.3945.130 Safari/537.36",
    "Referer": "https://www.bilibili.com/"
    }
    async with aiohttp.request('GET', url=url, headers=DEFAULT_HEADERS) as resp:
        return await resp.json(encoding='utf-8')


# async def Get(url):
#     """简单粗暴的请求模块"""
#     start = time.time()
#     DEFAULT_HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                   "Chrome/79.0.3945.130 Safari/537.36",
#     "Referer": "https://www.bilibili.com/"
#     }

#     r = requests.get(url, headers=DEFAULT_HEADERS)
#     r.encoding='utf-8'
#     print(time.time()-start)
#     return r.json()

async def read_config():
    """读取用户注册信息"""
    try:
        with open(get_path('config.json'), encoding='utf-8-sig') as f:
            config = json.loads(f.read())
    except FileNotFoundError:
        config = {"status": {}, "uid": {}, "groups": {}, "users": {}, "dynamic": {"uid_list": [], "index": 0}, 'live': {'uid_list': [], 'index': 0}}
    return config

async def update_config(config):
    """更新注册信息"""
    with open(get_path('config.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(config, ensure_ascii=False, indent=4))

def get_path(name):
    """获取数据文件绝对路径"""
    f_path = path.abspath(path.join('data', 'dd_bot', name))
    return f_path

# def log(func):
#     """捕捉错误并输出日志（logger定义在bot.py）"""
#     @functools.wraps(func)
#     async def wrapper(*args, **kw):
#         try:
#             r = await func(*args, **kw)
#             return r
#         except:
#             logger.error(traceback.format_exc())
#     return wrapper

# def restart():
#     # python = sys.executable
#     # print(sys.argv)
#     # os.execl(python, python, * sys.argv)
#     sys.exit()