import nonebot
from nonebot.adapters.cqhttp import Bot
from nonebot.log import default_format, logger


logger.add(
    "logs/error.log",
    rotation="00:00",
    retention="1 week",
    diagnose=False,
    level="DEBUG",
    format=default_format,
    encoding="utf-8",
)

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter("cqhttp", Bot)

nonebot.load_from_toml("pyproject.toml")

# Modify some config / config depends on loaded configs
#
# config = driver.config
# do something...


if __name__ == "__main__":
    nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
