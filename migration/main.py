import shutil
from pathlib import Path

from aerich import Command
from tortoise import run_async


def get_config(version=""):
    if version:
        name = f"models_{version}"
    else:
        name = "models"
    return {
        "connections": {"default": "sqlite://test.sqlite3"},
        "apps": {
            "models": {
                "models": [f"models.{name}", "aerich.models"],
                "default_connection": "default",
            },
        },
    }


def init():
    shutil.rmtree("./migrations")
    shutil.copy("./data.sqlite3", "./test.sqlite3")


OLD_CONFIG = get_config("135p3")
CONFIG = get_config()


async def main():
    init()

    # if not Path("./migrations").exists():
    command = Command(tortoise_config=OLD_CONFIG, app="models")
    await command.init()
    await command.init_db(True)

    command = Command(tortoise_config=CONFIG, app="models")
    await command.init()
    await command.migrate()
    # input()
    # await command.upgrade()


run_async(main())
