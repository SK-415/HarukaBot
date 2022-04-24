import base64
import os
import sys
from typing import Optional

from nonebot import get_driver
from nonebot.log import logger
from playwright.__main__ import main
from playwright.async_api import Browser, async_playwright

from .. import config

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
        # PC版网页：
        # page = await browser.new_page(device_scale_factor=2)
        # await page.goto(url, wait_until="networkidle", timeout=10000)
        # await page.set_viewport_size({"width": 2560, "height": 1080})
        # card = await page.query_selector(".card")

        # 移动端网页：
        page = await browser.new_page(
            viewport={"width": 360, "height": 780},
            user_agent="Mozilla/5.0 (Linux; Android 10; RMX1911) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36",
            device_scale_factor=3,
        )
        await page.goto(url, wait_until="networkidle", timeout=10000)
        content = await page.content()
        content = content.replace(
            '<div class="dyn-header__right"><div data-pos="follow" class="dyn-header__following"><span class="dyn-header__following__icon"></span><span class="dyn-header__following__text">关注</span></div></div>',
            "",
        )  # 去掉关注按钮
        content = content.replace(
            '<div class="dyn-card">',
            '<div class="dyn-card" style="font-family: sans-serif;">',
        )  # 字体问题：.dyn-class里font-family是PingFangSC-Regular，使用行内CSS覆盖掉它
        content = content.replace(
            '<div class="launch-app-btn dynamic-float-openapp"><div class="m-dynamic-float-openapp"><span>打开APP，查看更多精彩内容</span></div> <!----></div>',
            "",
        )  # 去掉打开APP的按钮，防止遮挡较长的动态
        await page.set_content(content)
        card = await page.query_selector(".dyn-card")
        assert card
        clip = await card.bounding_box()
        assert clip
        image = await page.screenshot(clip=clip, full_page=True)
        await page.close()
        return base64.b64encode(image).decode()
    except Exception:
        if page:
            await page.close()
        raise


def install():
    """自动安装、更新 Chromium"""

    def restore_env():
        del os.environ["PLAYWRIGHT_DOWNLOAD_HOST"]
        if config.haruka_proxy:
            del os.environ["HTTPS_PROXY"]
        if original_proxy is not None:
            os.environ["HTTPS_PROXY"] = original_proxy

    logger.info("检查 Chromium 更新")
    sys.argv = ["", "install", "chromium"]
    original_proxy = os.environ.get("HTTPS_PROXY")
    if config.haruka_proxy:
        os.environ["HTTPS_PROXY"] = config.haruka_proxy
    os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://playwright.sk415.workers.dev"
    success = False
    try:
        main()
    except SystemExit as e:
        if e.code == 0:
            success = True
    if not success:
        logger.info("Chromium 更新失败，尝试从原始仓库下载，速度较慢")
        os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = ""
        try:
            main()
        except SystemExit as e:
            if e.code != 0:
                restore_env()
                raise RuntimeError("未知错误，Chromium 下载失败")
    restore_env()


async def check_playwright_env():
    """检查 Playwright 依赖"""
    logger.info("检查 Playwright 依赖")
    try:
        async with async_playwright() as p:
            await p.chromium.launch()
    except Exception:
        raise ImportError(
            "加载失败，Playwright 依赖不全，"
            "解决方法：https://haruka-bot.sk415.icu/faq.html#playwright-依赖不全"
        )


get_driver().on_startup(init)
