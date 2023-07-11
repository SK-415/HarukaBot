import asyncio
import contextlib
import os
import re
import sys
from pathlib import Path
from typing import Optional

from nonebot.log import logger
from aunly_captcha_solver import CaptchaInfer
from playwright.__main__ import main
from playwright.async_api import BrowserContext, async_playwright, Page

from ..config import plugin_config
from .fonts_provider import fill_font
from ..utils import get_path

_browser: Optional[BrowserContext] = None
mobile_js = Path(__file__).parent.joinpath("mobile.js")


async def init_browser(proxy=plugin_config.haruka_proxy, **kwargs) -> BrowserContext:
    logger.info("初始化浏览器")
    if proxy:
        kwargs["proxy"] = {"server": proxy}
    global _browser
    p = await async_playwright().start()
    browser_data = Path(get_path("browser"))
    browser_data.mkdir(parents=True, exist_ok=True)
    browser_context = await p.chromium.launch_persistent_context(
        browser_data,
        user_agent=plugin_config.haruka_browser_ua
        or (
            (
                "Mozilla/5.0 (Linux; Android 10; RMX1911) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36"
            )
            if plugin_config.haruka_screenshot_style.lower() == "mobile"
            else None
        ),
        device_scale_factor=2,
        timeout=plugin_config.haruka_dynamic_timeout * 1000,
        **kwargs,
    )
    if plugin_config.haruka_screenshot_style.lower() != "mobile":
        await browser_context.add_cookies(
            [
                {
                    "name": "hit-dyn-v2",
                    "value": "1",
                    "domain": ".bilibili.com",
                    "path": "/",
                }
            ]
        )
    _browser = browser_context
    return _browser


async def get_browser() -> BrowserContext:
    global _browser
    if not _browser:
        _browser = await init_browser()
    return _browser


async def get_dynamic_screenshot(dynamic_id, style=plugin_config.haruka_screenshot_style):
    """获取动态截图"""
    image: Optional[bytes] = None
    err = ""
    for i in range(3):
        browser = await get_browser()
        page = await browser.new_page()
        try:
            # if style.lower() == "mobile":
            #     page, clip = await get_dynamic_screenshot_mobile(dynamic_id, page)
            # else:
            #     page, clip = await get_dynamic_screenshot_pc(dynamic_id, page)
            page, clip = await get_dynamic_screenshot_mobile(dynamic_id, page)
            clip["height"] = min(clip["height"], 32766)
            return (
                await page.screenshot(clip=clip, full_page=True, type="jpeg", quality=98),
                None,
            )
        except TimeoutError:
            logger.warning(f"截图超时，重试 {i + 1}/3")
            err = "截图超时"
        except Notfound:
            logger.error(f"动态 {dynamic_id} 不存在")
            err = "动态不存在"
        except AssertionError:
            logger.error(f"动态 {dynamic_id} 截图失败")
            err = "网页元素获取失败"
            image = await page.screenshot(full_page=True, type="jpeg", quality=80)
        except Exception as e:
            if "bilibili.com/404" in page.url:
                logger.error(f"动态 {dynamic_id} 不存在")
                err = "动态不存在"
                break
            elif "waiting until" in str(e):
                logger.error(f"动态 {dynamic_id} 截图超时")
                err = "截图超时"
            else:
                logger.exception(f"动态 {dynamic_id} 截图失败")
                err = "截图失败"
                with contextlib.suppress(Exception):
                    image = await page.screenshot(full_page=True, type="jpeg", quality=80)
        finally:
            with contextlib.suppress(Exception):
                await page.close()
    return image, err


async def get_dynamic_screenshot_mobile(dynamic_id, page: Page):
    """移动端动态截图"""
    url = f"https://m.bilibili.com/dynamic/{dynamic_id}"
    await page.set_viewport_size({"width": 460, "height": 780})
    await page.route(re.compile("^https://static.graiax/fonts/(.+)$"), fill_font)
    if plugin_config.haruka_captcha_address:
        captcha = CaptchaInfer(
            plugin_config.haruka_captcha_address, plugin_config.haruka_captcha_token
        )
        page = await captcha.solve_captcha(page, url)
    else:
        await page.goto(url, wait_until="networkidle")
    # 动态被删除或者进审核了
    if page.url == "https://m.bilibili.com/404":
        raise Notfound
    # await page.add_script_tag(
    #     content=
    #     # 去除打开app按钮
    #     "document.getElementsByClassName('m-dynamic-float-openapp').forEach(v=>v.remove());"
    #     # 去除关注按钮
    #     "document.getElementsByClassName('dyn-header__following').forEach(v=>v.remove());"
    #     # 修复字体与换行问题
    #     "const dyn=document.getElementsByClassName('dyn-card')[0];"
    #     "dyn.style.fontFamily='Noto Sans CJK SC, sans-serif';"
    #     "dyn.style.overflowWrap='break-word'"
    # )

    await page.wait_for_load_state(state="domcontentloaded")
    await page.wait_for_selector(".b-img__inner, .dyn-header__author__face", state="visible")

    await page.add_script_tag(path=mobile_js)

    await page.evaluate(
        f'setFont("{plugin_config.haruka_dynamic_font}", '
        f'"{plugin_config.haruka_dynamic_font_source}")'
        if plugin_config.haruka_dynamic_font
        else "setFont()"
    )
    await page.wait_for_function(
        f"getMobileStyle({'true' if plugin_config.haruka_dynamic_big_image else 'false'})"
    )

    await page.wait_for_load_state("networkidle")
    await page.wait_for_load_state("domcontentloaded")

    await page.wait_for_timeout(
        1000 if plugin_config.haruka_dynamic_font_source == "remote" else 200
    )

    # 判断字体是否加载完成
    need_wait = ["imageComplete", "fontsLoaded"]
    await asyncio.gather(*[page.wait_for_function(f"{i}()") for i in need_wait])

    card = await page.query_selector(".opus-modules" if "opus" in page.url else ".dyn-card")
    assert card
    clip = await card.bounding_box()
    assert clip
    return page, clip


async def get_dynamic_screenshot_pc(dynamic_id, page: Page):
    """电脑端动态截图"""
    url = f"https://t.bilibili.com/{dynamic_id}"
    await page.set_viewport_size({"width": 2560, "height": 1080})
    await page.goto(url, wait_until="networkidle")
    # 动态被删除或者进审核了
    if page.url == "https://www.bilibili.com/404":
        raise Notfound
    card = await page.query_selector(".card")
    assert card
    clip = await card.bounding_box()
    assert clip
    bar = await page.query_selector(".bili-dyn-action__icon")
    assert bar
    bar_bound = await bar.bounding_box()
    assert bar_bound
    clip["height"] = bar_bound["y"] - clip["y"]
    return page, clip


def install():
    """自动安装、更新 Chromium"""

    def restore_env():
        del os.environ["PLAYWRIGHT_DOWNLOAD_HOST"]
        if plugin_config.haruka_proxy:
            del os.environ["HTTPS_PROXY"]
        if original_proxy is not None:
            os.environ["HTTPS_PROXY"] = original_proxy

    logger.info("检查 Chromium 更新")
    sys.argv = ["", "install", "chromium"]
    original_proxy = os.environ.get("HTTPS_PROXY")
    if plugin_config.haruka_proxy:
        os.environ["HTTPS_PROXY"] = plugin_config.haruka_proxy
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
            "加载失败，Playwright 依赖不全，" "解决方法：https://haruka-bot.sk415.icu/faq.html#playwright-依赖不全"
        )


class Notfound(Exception):
    pass
