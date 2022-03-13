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


async def get_dynamic_screenshot(dynamic):
    browser = await get_browser()
    page = None
    try:
        page = await browser.new_page(device_scale_factor=2)
        await page.goto("file://" + str(Path.cwd()/"dynamic_analysis"/"dynamic_card.html"))
        await page.evaluate("""
                    (card_dic)=>{
                    window.card = card_dic
                     //先设置一下头像,昵称,时间,二维码,认证图标
            user_info_process(card);
            //对文字内容进行处理
            dynamic_text_process(card.desc.type, JSON.parse(card.card), 0, ".dynamic-text");
            add_on_card_info(card, 0);
            //找出转发内容所在的div,因为这个div背景颜色和其他的div不太一样
            //这个div的默认display为none,当动态类型为转发的时候将其display改为block
            var repost = $(".repost");
            switch (card.desc.type) {
                //转发的动态
                case 1:
                    //对转发部分进行处理
                    //先让转发内容所在的div显示出来
                    repost.css("display", "block")
                    repost_process()
                    break;
                //发送了一条带图片的动态
                case 2:
                    //对图片进行处理
                    pic_process(JSON.parse(card.card).item.pictures, ".dynamic-pic");
                    break
                //发送了一条纯文字动态
                case 4:
                    //可能有投票,也可能有其他东西,但是只见过投票所以其他的以后有时间再加
                    vote_process(card.desc.type, JSON.parse(card.card), 0)
                    break
                //发送了新投稿视频
                case 8:
                    video_process(card, 0);
                    break;
                //发送了专栏
                case 64:
                    //对专栏进行处理
                    article_process(JSON.parse(card.card), 0);
                    break;
                //音乐
                case 256:
                    music_process(JSON.parse(card.card), 0)
                    break;
                //挂件
                case 2048:
                //漫画
                case 2049:
                    other_process(JSON.parse(card.card), 0);
                    break;
            }
                    }
                    """, dynamic)
        await page.wait_for_load_state(state="networkidle", timeout=1000)
        image = await page.locator(".main-card").screenshot(type="jpeg", quality=100)
        await page.close()
        return base64.b64encode(image).decode()
    except Exception:
        if page:
            await page.close()
        raise


def delete_pyppeteer():
    """删除 Pyppeteer 遗留的 Chromium"""
    dir = Path(AppDirs("pyppeteer").user_data_dir)
    if not dir.exists():
        return

    if not config.haruka_delete_pyppeteer:
        logger.info(
            "检测到 Pyppeteer 依赖（约 300 M），"
            "新版 HarukaBot 已经不需要这些文件了。"
            "如果没有其他程序依赖 Pyppeteer，请在 '.env.*' 中设置"
            " 'HARUKA_DELETE_PYPPETEER=True' 并重启 Bot 后，将自动清除残留"
        )
    else:
        shutil.rmtree(dir)
        logger.info("已清理 Pyppeteer 依赖残留")


def install():
    """自动安装、更新 Chromium"""
    logger.info("正在检查 Chromium 更新")
    import sys
    from playwright.__main__ import main

    sys.argv = ["", "install", "chromium"]
    try:
        main()
    except SystemExit:
        pass


async def check_playwright_dependencies():
    """检查 Playwright 依赖"""
    logger.info("检查 Playwright 依赖，不完整将自动退出")
    await init()


get_driver().on_startup(delete_pyppeteer)
get_driver().on_startup(install)
get_driver().on_startup(check_playwright_dependencies)
