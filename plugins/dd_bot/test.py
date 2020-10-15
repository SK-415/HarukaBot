from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot, Event


test = on_command('test', rule=to_me(), priority=5)


@test.handle()
async def get_args(bot: Bot, event: Event, state: dict):
    await test.finish(int('test'))


# @add_uid.got('uid', prompt='请输入主播的uid')
# async def _(bot: Bot, event: Event, state: dict):