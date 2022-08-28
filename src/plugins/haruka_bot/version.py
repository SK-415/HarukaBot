from importlib.metadata import version

from packaging.version import Version

__version__ = version("haruka-bot")
VERSION = Version(__version__)
