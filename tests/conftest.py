from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator, Dict, Type

import pytest

if TYPE_CHECKING:
    from nonebot.matcher import Matcher


@pytest.fixture
def load_hb(nonebug_init: None) -> None:
    import sys

    sys.path.append(str(Path(__file__).parent.parent))

    import nonebot

    nonebot.load_plugins(str(Path("src") / "plugins")).pop()


@pytest.fixture
async def load_db(load_hb: None) -> AsyncGenerator[None, None]:
    import nonebot

    hb = nonebot.get_plugin("haruka_bot")
    assert hb is not None
    await hb.module.database.DB.init(":memory:")
    yield None
    from tortoise import Tortoise

    await Tortoise.close_connections()


@pytest.fixture
def matchers(load_db: None) -> Dict[str, Type["Matcher"]]:
    import nonebot

    hb = nonebot.get_plugin("haruka_bot")
    assert hb is not None
    return {
        matcher.module_name.split(".")[-1]: matcher  # type: ignore
        for matcher in hb.matcher
        if matcher is not None
    }
