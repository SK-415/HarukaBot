import asyncio
import traceback

from http.client import BadStatusLine
from nonebot.log import logger
from nonebot.exception import NoLogException
from pyppeteer import launch
from pyppeteer.errors import TimeoutError

from .config import Config


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
        self.uid = dynamic['desc']['user_profile']['info']['uid']
        self.name = dynamic['desc']['user_profile']['info'].get('uname', Config.get_name(self.uid))

    async def format(self):
        type_msg = {
            0: "发布了新动态",
            1: "转发了一条动态",
            8: "发布了新投稿",
            16: "发布了短视频",
            64: "发布了新专栏",
            256: "发布了新音频"
        }
        self.message = f"{self.name}{type_msg.get(self.type, type_msg[0])}：" +\
            f"\n\n传送门→{self.url}[CQ:image,file={self.img}]\n"

    async def get_screenshot(self, retry=3):
        browser = await launch(args=['--no-sandbox'])
        page = await browser.newPage()
        for i in range(retry + 1):
            try:
                await page.goto(self.url, waitUntil="networkidle0", timeout=10000)
                await page.setViewport(viewport={'width': 2560, 'height': 1080})
                card = await page.querySelector(".card")
                clip = await card.boundingBox()
                bar = await page.querySelector(".text-bar")
                bar_bound = await bar.boundingBox()
                clip['height'] = bar_bound['y'] - clip['y']
                self.img = "base64://" +\
                    await page.screenshot(clip=clip, encoding='base64')
                break
            except TimeoutError as e:
                logger.error(f"截图失败（连接超时） 已重试（{i}/{retry}）")
            except BadStatusLine as e:
                logger.error(f"截图失败（连接错误） 已重试（{i}/{retry}）")
            except Exception as e:
                logger.error("截图失败（未知错误），以下为错误日志")
                logger.error(traceback(e))
                await browser.close()
                raise
            finally:
                if i == retry:
                    try:
                        getattr(self, 'img')
                    except AttributeError:
                        logger.error("已达到重试上限，将在下个轮询中重新尝试")
                        await browser.close()
                        raise
            await asyncio.sleep(0.1)
        await browser.close()
