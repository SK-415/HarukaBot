from nonebot import get_driver
from nonebot.plugin.manager import PluginLoader

from .config import Config

try:
    global_config = get_driver().config
    config = Config(**global_config.dict())
    if isinstance(globals()['__loader__'], PluginLoader):
        from . import plugins
    else:
        from . import database
except ValueError:
    pass

from .version import VERSION, __version__
