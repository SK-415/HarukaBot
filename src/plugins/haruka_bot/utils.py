import asyncio
import os
import traceback
from os import path

import httpx
import nonebot
from nonebot import get_driver
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.log import logger
from nonebot.permission import GROUP_ADMIN, GROUP_OWNER, SUPERUSER
from nonebot.rule import Rule

# 更换 Chromium 下载地址为非 https 淘宝源
os.environ['PYPPETEER_DOWNLOAD_HOST'] = 'http://npm.taobao.org/mirrors'
# os.environ['PYPPETEER_DOWNLOAD_HOST'] = 'http://storage.googleapis.com'
from pyppeteer import launch # 不能删，隔壁 dynamic.py 还要调用的
from pyppeteer.chromium_downloader import check_chromium, download_chromium

# 检查 Chromium 是否下载
if not check_chromium():
    download_chromium()


class BiliAPI():
    def __init__(self) -> None:
        self.default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/79.0.3945.130 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
        }
        
    async def get(self, url, headers=None, decode=True):
        if not headers:
            headers = self.default_headers
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=headers)
        if decode:
            r.encoding = 'utf-8'
            return r.json()
        return r
    
    async def get_info(self, uid):
        url = f'https://api.bilibili.com/x/space/acc/info?mid={uid}'
        return (await self.get(url))['data']

    async def get_dynamic(self, uid):
        # need_top: {1: 带置顶, 0: 不带置顶}
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&offset_dynamic_id=0&need_top=0'
        return (await self.get(url))['data']
    
    async def get_live_info(self, uid):
        url = f'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={uid}'
        return (await self.get(url))['data']
        

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


async def permission_check(bot: Bot, event: Event, state: dict):
    from .config import Config
    config = Config()
    if event.detail_type == 'private':
        return True
    group_id = str(event.group_id)
    with Config() as config:
        if config.get_admin(group_id):
            return await (GROUP_ADMIN | GROUP_OWNER | SUPERUSER)(bot, event)
        return True

def to_me():
    config = get_driver().config
    if config.haruka_to_me != False:
        from nonebot.rule import to_me
        return to_me()
    async def _to_me(bot: Bot, event: Event, state: dict):
        return True
    return Rule(_to_me)


async def safe_send(bot: Bot, send_type, type_id, message):
    """发送出现错误时, 尝试重新发送, 并捕获异常且不会中断运行"""
    i = 0
    while True:
        try:
            i += 1
            return await send(bot, send_type, type_id, message)
        except:
            logger.error(traceback.format_exc())
            if i == 3:
                bot = await restart(bot)
                warning_msg = '检测到推送出现异常，已尝试自动重启，如仍有问题请向机器人管理员反馈'
                await send(bot, send_type, type_id, warning_msg)
                return await send(bot, send_type, type_id, message)
            await asyncio.sleep(0.1)

async def send(bot, send_type, type_id, message):
    return await bot.call_api('send_'+send_type+'_msg', **{
        'message': message,
        'user_id' if send_type == 'private' else 'group_id': type_id
        })

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
