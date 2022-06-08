import pkg_resources
# from importlib.metadata import version


# __version__ = version('haruka-bot')
# 照顾 3.8 以下用户，改用兼容性更高的方法检查版本
_dist: pkg_resources.Distribution = pkg_resources.get_distribution("haruka-bot")
__version__ = _dist.version
VERSION = _dist.parsed_version
