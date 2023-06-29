import contextlib
from typing import Optional, List

import httpx
from nonebot.log import logger
from playwright._impl._api_structures import Position
from playwright.async_api import Page, Response
from pydantic import BaseModel
from yarl import URL

from ..config import plugin_config


class CaptchaData(BaseModel):
    captcha_id: str
    points: List[List[int]]
    rectangles: List[List[int]]
    yolo_data: List[List[int]]
    time: int


class CaptchaResponse(BaseModel):
    code: int
    message: str
    data: Optional[CaptchaData]


async def resolve_captcha(url: str, page: Page) -> Page:
    captcha_image_body = ""
    last_captcha_id = ""
    captcha_result = None

    async def captcha_image_url_callback(response: Response):
        nonlocal captcha_image_body
        logger.debug(f"[Captcha] Get captcha image url: {response.url}")
        captcha_image_body = await response.body()

    async def captcha_result_callback(response: Response):
        nonlocal captcha_result, last_captcha_id
        logger.debug(f"[Captcha] Get captcha result: {response.url}")
        captcha_resp = await response.text()
        logger.debug(f"[Captcha] Result: {captcha_resp}")
        if '"result": "success"' in captcha_resp:
            logger.success("[Captcha] 验证码 Callback 验证成功")
            captcha_result = True
        elif '"result": "click"' in captcha_resp:
            pass
        else:
            if last_captcha_id:
                logger.warning(f"[Captcha] 验证码 Callback 验证失败，正在上报：{last_captcha_id}")
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{captcha_baseurl}/report",
                        json={"captcha_id": last_captcha_id},
                    )
                last_captcha_id = ""
            captcha_result = False

    captcha_address = URL(plugin_config.haruka_captcha_address)
    page.on(
        "response",
        lambda response: captcha_image_url_callback(response)
        if response.url.startswith("https://static.geetest.com/captcha_v3/")
        else None,
    )
    page.on(
        "response",
        lambda response: captcha_result_callback(response)
        if response.url.startswith("https://api.geetest.com/ajax.php")
        else None,
    )

    with contextlib.suppress(TimeoutError):
        await page.goto(
            url,
            wait_until="networkidle",
            timeout=plugin_config.haruka_dynamic_timeout * 1000,
        )

    captcha_baseurl = f"{captcha_address.scheme}://{captcha_address.host}:{captcha_address.port}/captcha/select"
    while captcha_image_body or captcha_result is False:
        logger.warning("[Captcha] 需要人机验证，正在尝试自动解决验证码")
        captcha_image = await page.query_selector(".geetest_item_img")
        assert captcha_image
        captcha_size = await captcha_image.bounding_box()
        assert captcha_size
        origin_image_size = 344, 384

        async with httpx.AsyncClient() as client:
            captcha_req = await client.post(
                f"{captcha_baseurl}/bytes",
                timeout=10,
                files={"img_file": captcha_image_body},
            )
            captcha_req = CaptchaResponse(**captcha_req.json())
            logger.debug(f"[Captcha] Get Resolve Result: {captcha_req}")
            assert captcha_req.data
            last_captcha_id = captcha_req.data.captcha_id
        if captcha_req.data:
            click_points: List[List[int]] = captcha_req.data.points
            logger.warning(f"[Captcha] 识别到 {len(click_points)} 个坐标，正在点击")
            # 根据原图大小和截图大小计算缩放比例，然后计算出正确的需要点击的位置
            for point in click_points:
                real_click_points = {
                    "x": point[0] * captcha_size["width"] / origin_image_size[0],
                    "y": point[1] * captcha_size["height"] / origin_image_size[1],
                }
                await captcha_image.click(position=Position(**real_click_points))
                await page.wait_for_timeout(800)
            await page.click("text=确认")
            geetest_up = await page.wait_for_selector(".geetest_up", state="visible")
            if not geetest_up:
                logger.warning("[Captcha] 未检测到验证码验证结果，正在重试")
                continue
            geetest_result = await geetest_up.text_content()
            assert geetest_result
            logger.debug(f"[Captcha] Geetest result: {geetest_result}")
            if "验证成功" in geetest_result:
                logger.success("[Captcha] 极验网页 Tip 验证成功")
                captcha_image_body = ""
                await page.wait_for_timeout(2000)
            else:
                logger.warning("[Captcha] 极验验证失败，正在重试")

    return page
