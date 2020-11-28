from collections import Counter
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.permission import GROUP_ADMIN, PRIVATE_FRIEND, SUPERUSER, GROUP_OWNER
from .utils import Config


async def permission_check(bot: Bot, event: Event, state: dict):
    config = Config()
    await config.read()
    if event.detail_type == 'group':
        group_id = str(event.group_id)
        if True if group_id not in config.config['groups'] else config.config['groups'][group_id]['admin']:
            is_admin = await GROUP_ADMIN(bot, event) or await GROUP_OWNER(bot, event) or await PRIVATE_FRIEND(bot, event) or await SUPERUSER(bot, event)
            if is_admin:
                return True
            else:
                # await bot.send(event, '权限不足，无法使用')
                return False
        else:
            return True
    else:
        return True # 私聊默认返回 True


add_uid = on_command('添加主播', rule=to_me() & permission_check, priority=5)

@add_uid.handle()
async def get_args(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@add_uid.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    config = Config(event)
    await add_uid.finish(await config.add_uid(uid))


delete_uid = on_command('删除主播', rule=to_me() & permission_check, priority=5)

@delete_uid.handle()
async def get_args(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@delete_uid.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    config = Config(event)
    await delete_uid.finish(await config.delete_uid(uid))


uid_list = on_command('主播列表', rule=to_me() & permission_check, priority=5)

@uid_list.handle()
async def _(bot: Bot, event: Event, state: dict):
    config = Config(event)    
    await uid_list.finish(await config.uid_list())


dynamic_on = on_command('开启动态', rule=to_me() & permission_check, priority=5)

@dynamic_on.handle()
async def handle_first_recive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@dynamic_on.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    config = Config(event)
    msg = await config.set('dynamic', uid, True)
    await dynamic_on.finish(msg.replace('name', '开启动态'))


dynamic_off = on_command('关闭动态', rule=to_me() & permission_check, priority=5)

@dynamic_off.handle()
async def handle_first_recive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@dynamic_off.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    config = Config(event)
    msg = await config.set('dynamic', uid, False)
    await dynamic_off.finish(msg.replace('name', '关闭动态'))


live_on = on_command('开启直播', rule=to_me() & permission_check, priority=5)

@live_on.handle()
async def handle_first_recive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@live_on.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    config = Config(event)
    msg = await config.set('live', uid, True)
    await live_on.finish(msg.replace('name', '开启直播'))
    

live_off = on_command('关闭直播', rule=to_me() & permission_check, priority=5)

@live_off.handle()
async def handle_first_recive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@live_off.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    config = Config(event)
    msg = await config.set('live', uid, False)
    await live_off.finish(msg.replace('name', '关闭直播'))


at_on = on_command('开启全体', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | PRIVATE_FRIEND | SUPERUSER, 
    priority=5)

@at_on.handle()
async def handle_first_recive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@at_on.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    config = Config(event)
    msg = await config.set('at', uid, True)
    await at_on.finish(msg.replace('name', '开启全体'))


at_off = on_command('关闭全体', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | PRIVATE_FRIEND | SUPERUSER, 
    priority=5)

@at_off.handle()
async def handle_first_recive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@at_off.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    config = Config(event)
    msg = await config.set('at', uid, False)
    await at_off.finish(msg.replace('name', '关闭全体'))


permission_on = on_command('开启权限', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | PRIVATE_FRIEND | SUPERUSER, 
    priority=5)

@permission_on.handle()
async def _(bot: Bot, event: Event, state: dict):
    config = Config(event)
    msg = await config.set_permission(True)
    await permission_on.finish(msg.replace('name', '开启权限'))


permission_off = on_command('关闭权限', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | PRIVATE_FRIEND | SUPERUSER, 
    priority=5)

@permission_off.handle()
async def _(bot: Bot, event: Event, state: dict):
    config = Config(event)
    msg = await config.set_permission(False)
    await permission_on.finish(msg.replace('name', '关闭权限'))


fix_config = on_command('更新配置', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | PRIVATE_FRIEND | SUPERUSER, 
    priority=5)

@fix_config.handle()
async def _(bot: Bot, event: Event, state: dict):
    config = Config()
    old_config = await config.read()
    await config.backup()
    await config.update(config.new())
    
    for config_type in ['groups', 'users']:
        config.type = config_type
        for type_id, type_config in old_config[config_type].items():
            config.type_id = type_id
            uids = type_config['uid']
            for uid, sets in uids.items():
                config.id = old_config['uid'][uid][config.type][config.type_id]
                await config.add_uid(uid)
                for func, status in sets.items():
                    await config.set(func, uid, status)
            if 'admin' in type_config and not type_config['admin']:
                await config.set_permission(False)
    await fix_config.finish('更新完成')
    