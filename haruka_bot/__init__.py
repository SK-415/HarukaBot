from nonebot import get_driver
from nonebot.plugin.manager import PluginLoader

from .config import Config

if isinstance(globals()["__loader__"], PluginLoader):
    global_config = get_driver().config
    config = Config.parse_obj(global_config)
    from .utils import on_startup

    on_startup()

    from . import plugins  # noqa: F401

from .version import VERSION, __version__  # noqa: F401
