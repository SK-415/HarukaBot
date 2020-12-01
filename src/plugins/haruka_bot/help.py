from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot, Event


func_list = """DD机目前支持的功能有：

  主播列表
  开启权限
  关闭权限
  添加主播 uid
  删除主播 uid
  开启动态 uid
  关闭动态 uid
  开启直播 uid
  关闭直播 uid
  开启全体 uid
  关闭全体 uid


命令中的uid需要替换为对应主播的uid，注意是uid不是直播间id

群聊默认开启权限，只有管理员或机器人主人才能触发指令

所有群聊/私聊的推送都是分开的，在哪里添加就只会在哪里推送
"""


help = on_command('帮助', rule=to_me(), priority=5)

@help.handle()
async def _(bot: Bot, event: Event, state: dict):
    await help.finish(func_list)

