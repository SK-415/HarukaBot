import httpx

from yarl import URL
from pathlib import Path
from nonebot.log import logger
from playwright.async_api import Request, Route


font_path = Path("fonts")
font_mime_map = {
    "collection": "font/collection",
    "otf": "font/otf",
    "sfnt": "font/sfnt",
    "ttf": "font/ttf",
    "woff": "font/woff",
    "woff2": "font/woff2",
}
font_path.mkdir(parents=True, exist_ok=True)


async def get_font(font: str):
    logger.debug(f"font: {font}")
    url = URL(font)
    if url.is_absolute():
        if font_path.joinpath(url.name).exists():
            logger.debug(f"Font {url.name} found in local")
            return font_path.joinpath(url.name)
        else:
            logger.warning(f"字体 {font} 不存在，尝试从网络获取")
            async with httpx.AsyncClient() as client:
                resp = await client.get(font)
                if resp.status_code != 200:
                    raise ConnectionError(f"字体 {font} 获取失败")
                font_path.joinpath(url.name).write_bytes(resp.content)
                return font_path.joinpath(url.name)
    else:
        if not font_path.joinpath(font).exists():
            raise FileNotFoundError(f"字体 {font} 不存在")
        logger.debug(f"Font {font} found in local")
        return font_path.joinpath(font)


async def fill_font(route: Route, request: Request):
    url = URL(request.url)
    if not url.is_absolute():
        raise ValueError("字体地址不合法")
    try:
        logger.debug(f"Font {url.name} requested")
        await route.fulfill(
            path=await get_font(url.query["name"]),
            content_type=font_mime_map.get(url.suffix, None),
        )
        return
    except Exception:
        logger.debug(f"can't get font {url.name}")
        await route.fallback()
