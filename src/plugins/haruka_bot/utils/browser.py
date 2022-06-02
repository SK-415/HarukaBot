import base64
import os
import sys
from typing import Optional

from nonebot import get_driver
from nonebot.log import logger
from playwright.__main__ import main
from playwright.async_api import BrowserContext, async_playwright

from .. import config

_browser: Optional[BrowserContext] = None


async def init(**kwargs) -> BrowserContext:
    global _browser
    p = await async_playwright().start()
    browser = await p.chromium.launch(**kwargs)
    _browser = await browser.new_context(
        device_scale_factor=2,
        # 移动端
        user_agent=(
            "Mozilla/5.0 (Linux; Android 10; RMX1911) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36"
        ),
    )
    # 电脑端
    # await _browser.add_cookies(
    #     [{"name": "hit-dyn-v2", "value": "1", "domain": ".bilibili.com", "path": "/"}]
    # )

    return _browser


async def get_browser(**kwargs) -> BrowserContext:
    return _browser or await init(**kwargs)


async def get_dynamic_screenshot(url):
    browser = await get_browser()
    page = None
    try:
        # 电脑端
        # page = await browser.new_page()
        # await page.goto(url, wait_until="networkidle", timeout=10000)
        # await page.set_viewport_size({"width": 2560, "height": 1080})
        # card = await page.query_selector(".card")
        # assert card
        # clip = await card.bounding_box()
        # assert clip
        # bar = await page.query_selector(".bili-dyn-action__icon")
        # assert bar
        # bar_bound = await bar.bounding_box()
        # assert bar_bound
        # clip["height"] = bar_bound["y"] - clip["y"]

        # 移动端
        page = await browser.new_page()
        await page.set_viewport_size({"width": 360, "height": 780})
        await page.goto(url, wait_until="networkidle", timeout=10000)
        content = await page.content()
        content = content.replace(
            '<div class="dyn-header__right"><div data-pos="follow" class="dyn-header__following"><span class="dyn-header__following__icon"></span><span class="dyn-header__following__text">关注</span></div></div>',
            "",
        )  # 去掉关注按钮

        content = content.replace(
            '<div class="dyn-card">',
            '<div class="dyn-card" style="font-family: sans-serif; overflow-wrap: break-word;">',
        )
        # 1. 字体问题：.dyn-class里font-family是PingFangSC-Regular，使用行内CSS覆盖掉它
        # 2. 换行问题：遇到太长的内容（长单词、某些长链接等）允许强制换行，防止溢出
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
    # TODO 检查 google 可访问性
    if config.haruka_proxy:
        os.environ["HTTPS_PROXY"] = config.haruka_proxy
    os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://playwright.sk415.icu"
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
