from nonebot.plugin.manager import PluginLoader

if isinstance(globals()["__loader__"], PluginLoader):
    from .utils import on_startup

    on_startup()

    from . import plugins  # noqa: F401

from .version import VERSION, __version__  # noqa: F401
