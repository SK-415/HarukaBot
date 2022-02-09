import asyncio
import platform
from uvicorn.loops import asyncio as _asyncio
from uvicorn import config
from nonebot.log import logger


def asyncio_setup():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


@property
def should_reload(self):
    return False


if platform.system() == "Windows":
    _asyncio.asyncio_setup = asyncio_setup
    config.Config.should_reload = should_reload  # type: ignore
    logger.warning("检测到当前为 Windows 系统，已自动注入猴子补丁")
