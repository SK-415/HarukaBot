import asyncio
import base64
import traceback
from os import path

from nonebot.log import logger

from .utils import get_path, launch


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
        try:
            self.name = dynamic['desc']['user_profile']['info']['uname']
        except:
            logger.error("uname 错误，一下为 dynamic 内容")
            logger.error(dynamic)
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
