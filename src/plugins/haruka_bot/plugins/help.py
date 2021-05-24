from nonebot import on_command
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import MessageEvent
from nonebot.typing import T_State

from ..utils import to_me
from ..version import __version__


# TODO 使用 doc 代替命令名列表
func_list = [
    '主播列表', '开启权限', '关闭权限', '添加主播', '删除主播', '开启动态',
    '关闭动态', '开启直播', '关闭直播', '开启全体', '关闭全体', '版本信息']


help = on_command('帮助', rule=to_me(), priority=5)

@help.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    message = "DD机目前支持的功能有：\n\n"
    for name in func_list:
        message += name
        if not name.endswith(('列表', '权限', '版本信息')):
            message += " uid"
        message += '\n'
    message += "\n命令中的uid需要替换为对应主播的uid，注意是uid不是直播间id\n" + \
        "\n群聊默认开启权限，只有管理员或机器人主人才能触发指令\n" + \
        "\n所有群聊/私聊的推送都是分开的，在哪里添加就会在哪里推送"
    await help.finish(message)