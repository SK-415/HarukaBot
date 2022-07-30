import pytest
from nonebug import App
from typing import TYPE_CHECKING, Dict, Any
from utils import fake_private_event

if TYPE_CHECKING:
    from nonebot.plugin import Plugin


@pytest.mark.asyncio
async def test_sub1(app: App, matchers):
    async with app.test_matcher(matchers["add_sub"]) as ctx:
        bot = ctx.create_bot()
        event = fake_private_event("关注 1")

        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "已关注 bishi（1） ", True)


@pytest.mark.asyncio
async def test_sub2(app: App, matchers):
    async with app.test_matcher(matchers["add_sub"]) as ctx:
        bot = ctx.create_bot()
        event = fake_private_event("关注 1")

        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "bishi（1）已经关注了 ", True)


@pytest.mark.asyncio
async def test_sub3(app: App, matchers):
    matcher = matchers["add_sub"]
    await test_matcher(app, matcher, {}, "关注 1", "bishi（1）已经关注了 ")


async def test_matcher(app: App, matcher, bot: Dict, send_msg, receive_msg):
    async with app.test_matcher(matcher) as ctx:
        bot = ctx.create_bot(**bot)  # type: ignore
        event = fake_private_event(send_msg)
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, receive_msg, True)
