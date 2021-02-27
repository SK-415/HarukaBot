import nonebot

try:
    nonebot.get_driver()
    from . import utils
    from . import config_manager
    from . import live_pusher
    # from . import dynamic_pusher
    from . import keep_online
    from . import auto_agree
    from . import new_dynamic
except ValueError:
    pass

from .version import __version__, VERSION
