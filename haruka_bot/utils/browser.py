import os
import sys
from typing import Optional

from nonebot import get_driver
from nonebot.log import logger
from playwright.__main__ import main
from playwright.async_api import Browser, async_playwright

from .. import config

_browser: Optional[Browser] = None


async def init_browser(proxy=config.haruka_proxy, **kwargs) -> Browser:
    if proxy:
        kwargs["proxy"] = {"server": proxy}
    global _browser
    p = await async_playwright().start()
    _browser = await p.chromium.launch(**kwargs)
    return _browser


async def get_browser() -> Browser:
    assert _browser
    return _browser


async def get_dynamic_screenshot(dynamic_id, style=config.haruka_screenshot_style):
    """获取动态截图"""
    if style.lower() == "mobile":
        return await get_dynamic_screenshot_mobile(dynamic_id)
    else:
        return await get_dynamic_screenshot_pc(dynamic_id)


async def get_dynamic_screenshot_mobile(dynamic_id):
    """移动端动态截图"""
    url = f"https://m.bilibili.com/dynamic/{dynamic_id}"
    browser = await get_browser()
    page = await browser.new_page(
        device_scale_factor=2,
        user_agent=(
            "Mozilla/5.0 (Linux; Android 10; RMX1911) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36"
        ),
        viewport={"width": 360, "height": 780},
    )
    try:
        await page.goto(url, wait_until="networkidle", timeout=10000)
        # 动态被删除或者进审核了
        if page.url == "https://m.bilibili.com/404":
            return None
        await page.add_script_tag(
            content=
            # 去除打开app按钮
            "document.getElementsByClassName('launch-app-btn').forEach(v=>v.remove());"
            # 去除关注按钮
            "document.getElementsByClassName('dyn-header__following').forEach(v=>v.remove());"
            # 修复字体与换行问题
            "const dyn=document.getElementsByClassName('dyn-card')[0];"
            "dyn.style.fontFamily='Noto Sans CJK SC, sans-serif';"
            "dyn.style.overflowWrap='break-word'"
        )
        card = await page.query_selector(".dyn-card")
        assert card
        clip = await card.bounding_box()
        assert clip
        return await page.screenshot(clip=clip, full_page=True)
    except Exception:
        logger.exception(f"截取动态时发生错误：{url}")
        return await page.screenshot(full_page=True)
    finally:
        await page.close()


async def get_dynamic_screenshot_pc(dynamic_id):
    """电脑端动态截图"""
    url = f"https://t.bilibili.com/{dynamic_id}"
    browser = await get_browser()
    context = await browser.new_context(
        viewport={"width": 2560, "height": 1080},
        device_scale_factor=2,
    )
    await context.add_cookies(
        [
            {
                "name": "hit-dyn-v2",
                "value": "1",
                "domain": ".bilibili.com",
                "path": "/",
            }
        ]
    )
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=10000)
        # 动态被删除或者进审核了
        if page.url == "https://www.bilibili.com/404":
            return None
        card = await page.query_selector(".card")
        assert card
        clip = await card.bounding_box()
        assert clip
        bar = await page.query_selector(".bili-dyn-action__icon")
        assert bar
        bar_bound = await bar.bounding_box()
        assert bar_bound
        clip["height"] = bar_bound["y"] - clip["y"]
        return await page.screenshot(clip=clip, full_page=True)
    except Exception:
        logger.exception(f"截取动态时发生错误：{url}")
        return await page.screenshot(full_page=True)
    finally:
        await context.close()


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
    os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://npmmirror.com/mirrors/playwright/"
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


get_driver().on_startup(init_browser)
