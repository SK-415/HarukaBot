import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.log import default_format, logger

logger.add(
    "logs/error.log",
    rotation="00:00",
    retention="1 week",
    diagnose=False,
    level="ERROR",
    format=default_format,
    encoding="utf-8",
)


nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)


nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.run()
