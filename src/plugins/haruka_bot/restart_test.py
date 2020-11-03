import nonebot
from nonebot import scheduler, on_command
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.rule import to_me
from nonebot.log import logger
from .utils import safe_send


restart_test = on_command('try', rule=to_me(), priority=5)

# @scheduler.scheduled_job('cron', second='*/10', id='restart_test')
# @logger.catch

@restart_test.handle()
async def restart_test(bot: Bot, event: Event, state: dict):
    bot = nonebot.get_bots()['3424139009']
    await safe_send(bot, 'group', 1051522760, '测试')
