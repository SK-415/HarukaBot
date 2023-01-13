from playwright.async_api import Request, Route
from yarl import URL
from loguru import logger

from pathlib import Path

font_path = Path("font")

font_mime_map = {
    "collection": "font/collection",
    "otf": "font/otf",
    "sfnt": "font/sfnt",
    "ttf": "font/ttf",
    "woff": "font/woff",
    "woff2": "font/woff2",
}


async def fill_font(route: Route, request: Request):
    url = URL(request.url)
    if font_path.joinpath(url.name).exists():
        logger.debug(f"Font {url.name} found in local")
        await route.fulfill(
            path=font_path.joinpath(url.name),
            content_type=font_mime_map.get(url.suffix, None),
        )
        return
    await route.fallback()
