from pathlib import Path

import nonebot
from nonebot import get_driver

from .config import Config

try:
    global_config = get_driver().config
    config = Config(**global_config.dict())
    _sub_plugins = set()
    _sub_plugins |= nonebot.load_plugins(
        str((Path(__file__).parent / "plugins").resolve()))
except ValueError:
    pass

from .version import VERSION, __version__
