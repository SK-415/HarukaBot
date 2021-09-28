import base64
import shutil
from pathlib import Path
from typing import Optional

from appdirs import AppDirs
from nonebot import get_driver
from nonebot.log import logger
from playwright.async_api import Browser, async_playwright

from . import config

_browser: Optional[Browser] = None


async def init(**kwargs) -> Browser:
    global _browser
    browser = await async_playwright().start()
    _browser = await browser.chromium.launch(**kwargs)
    return _browser


async def get_browser(**kwargs) -> Browser:
    return _browser or await init(**kwargs)

 
async def get_dynamic_screenshot(url):
    browser = await get_browser()
    page = None
    try:
        page = await browser.new_page(device_scale_factor=2)
        await page.goto(url, wait_until='networkidle', timeout=10000)
        await page.set_viewport_size({"width": 2560, "height": 1080})
        card = await page.query_selector(".card")
        assert card
        clip = await card.bounding_box()
        assert clip
        bar = await page.query_selector(".text-bar")
        assert bar
        bar_bound = await bar.bounding_box()
        assert bar_bound
        clip['height'] = bar_bound['y'] - clip['y']
        image = await page.screenshot(clip=clip, full_page=True)
        await page.close()
        return base64.b64encode(image).decode()
    except Exception:
        if page:
            await page.close()
        raise


def install():
    """自动安装、更新 Chromium"""

    logger.info("正在检查 Chromium 更新")
    import sys
    from playwright.__main__ import main
    sys.argv = ['', 'install', 'chromium']
    try:
        main()
    except SystemExit:
        pass


def delete_pyppeteer():
    """删除 Pyppeteer 遗留的 Chromium"""

    dir = Path(AppDirs('pyppeteer').user_data_dir)
    if not dir.exists():
        return

    if not config.haruka_delete_pyppeteer:
        logger.info("检测到 Pyppeteer 依赖（约 300 M)，"
                    "新版 HarukaBot 已经不需要这些文件了。"
                    "如果没有其他程序依赖 Pyppeteer，请在 '.env.*' 中设置"
                    " 'HARUKA_DELETE_PYPPETEER=True' 并重启 Bot 后，将自动清除残留")
    else:
        shutil.rmtree(dir)
        logger.info("已清理 Pyppeteer 依赖残留")


get_driver().on_startup(delete_pyppeteer)
get_driver().on_startup(install)
