import nonebot

try:
    nonebot.get_driver()
    from . import utils
    from . import plugins
except ValueError:
    pass

from .version import __version__, VERSION
