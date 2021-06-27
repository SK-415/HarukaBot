import json
from pathlib import Path
from typing import Dict, List, Optional

from nonebot import get_driver
from nonebot.log import logger
from packaging.version import Version
from tortoise import Tortoise
from tortoise.query_utils import Q
from tortoise.queryset import QuerySet

from ..utils import get_path
from ..version import __version__
from .models import Group, Sub, User
from .models import Version as DBVersion

uid_list = {'live': {'list': [], 'index': 0},
            'dynamic': {'list': [], 'index': 0}}


class DB:
    """数据库交互类，与增删改查无关的部分不应该在这里面实现"""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @classmethod
    async def init(cls):
        from . import models
        await Tortoise.init(
            db_url=f"sqlite://{get_path('data.sqlite3')}",
            modules={'models': [locals()['models']]}
        )
        await Tortoise.generate_schemas()

    async def add_group(self, group_id, admin=True):
        """创建群设置"""
        
        if Group.filter(Q(id=group_id)).exists():
            # 权限开关已经创建过了
            return
        # TODO 自定义默认权限
        await Group.create(id=group_id, admin=admin)

    async def add_sub(self, uid, type_, type_id, bot_id, name, live=True,
                      dynamic=True, at=False) -> bool:
        """添加订阅"""
        
        if await self.get_sub(uid, type_, type_id):
            return False
        if not await self.get_user(uid):
            await self.add_user(uid, name)
        if type_ == 'group':
            await self.add_group(type_id)
        await Sub.create(
            uid=uid,
            type=type_,
            type_id=type_id,
            # TODO 自定义默认动态直播全体开关
            live=live,
            dynamic=dynamic,
            at=at,
            bot_id=bot_id
        )
        await self.update_uid_list()
        return True

    async def add_user(self, uid, name):
        """添加 UP 主信息"""

        await User.create(uid=uid, name=name)

    async def delete_group(self, group_id) -> bool:
        """删除群设置"""
        
        if await self.get_sub(type_='group', type_id=group_id):
            # 当前群还有订阅，不能删除
            return False
        await Group.filter(Q(id=group_id)).delete()
        return True

    async def delete_sub(self, uid, type_, type_id) -> bool:
        """删除指定订阅"""
        
        if not await self.get_sub(uid, type_, type_id):
            # 订阅不存在
            return False
        await self._get_subs(uid, type_, type_id).delete()
        await self.delete_user(uid)
        await self.update_uid_list()
        return True

    async def delete_sub_list(self, type_, type_id):
        "删除指定位置的推送列表"
        
        subs = self._get_subs(type_=type_, type_id=type_id)
        uids = [sub.uid async for sub in subs]
        await subs.delete()
        for uid in uids:
            await self.delete_user(uid)
        if type_ == 'group':
            await self.delete_group(type_id)
        await self.update_uid_list()

    async def delete_user(self, uid) -> bool:
        """删除 UP 主信息"""
        
        if await self.get_sub(uid):
            # 还存在该 UP 主订阅，不能删除
            return False
        await User.filter(Q(uid=uid)).delete()
        return True

    async def get_admin(self, group_id) -> bool:
        """获取指定群权限状态"""
        
        group = await Group.filter(Q(id=group_id)).first()
        if not group:
            return True
        return bool(group.admin)

    @classmethod
    async def get_name(cls, uid) -> Optional[str]:
        """获取 UP 主昵称"""

        user = await cls.get_user(uid)
        if user:
            return user.name
        return None

    async def get_push_list(self, uid, func) -> List[Sub]:
        """根据类型和 UID 获取需要推送的 QQ 列表"""
        
        return await self._get_subs(uid, **{func: True}).all()

    async def get_sub(self, uid=None, type_=None, type_id=None) -> Optional[Sub]:
        """获取指定位置的订阅信息"""
        
        return await self._get_subs(uid, type_, type_id).first()

    async def get_sub_list(self, type_, type_id) -> List[Sub]:
        """获取指定位置的推送列表"""
        
        return await self._get_subs(type_=type_, type_id=type_id).all()
        

    def _get_subs(self, uid=None, type_=None, type_id=None, live=None,
                       dynamic=None, at=None, bot_id=None) -> QuerySet[Sub]:
        """获取指定的订阅数据"""
        
        kw = locals()
        del kw['self']
        kw['type'] = kw.pop('type_')
        filters = [Q(**{key: value}) for key, value in kw.items()
                                     if value != None]
        return Sub.filter(Q(*filters, join_type='AND'))
        

    async def get_uid_list(self, func) -> List:
        """根据类型获取需要爬取的 UID 列表"""
        
        return uid_list[func]['list']        

    @classmethod
    async def get_user(cls, uid: int) -> Optional[User]:
        """获取 UP 主信息，没有就返回 None"""
        
        return await User.filter(Q(uid=uid)).first()

    async def _need_update(self):
        """根据版本号检查是否需要更新"""

        haruka_version = Version(__version__)
        db_version = await DBVersion.first()
        if not db_version:
            await DBVersion.create(version=__version__)
            return False
        db_version = Version(db_version.version)
        return haruka_version > db_version

    async def next_uid(self, func):
        """获取下一个要爬取的 UID"""
        
        func = uid_list[func]
        if func['list'] == []:
            return None

        if func['index'] >= len(func['list']):
            func['index'] = 1
            return func['list'][0]
        else:
            index = func['index']
            func['index'] += 1
            return func['list'][index]

    async def set_permission(self, group_id, switch) -> bool:
        """设置指定位置权限"""
        
        query = Group.filter(Q(id=group_id))
        group = await query.first()
        if not group:
            await Group.create(id=group_id, admin=switch)
            return True
        if group.admin == switch:
            return False
        await query.update(admin=switch)
        return True

    async def set_sub(self, conf, switch, uid=None, type_=None, type_id=None):
        """开关订阅设置"""

        subs = self._get_subs(uid, type_, type_id)
        if not await subs.exists():
            return False
        await subs.update(**{conf: switch})
        return True

    async def update_uid_list(self):
        """更新需要推送的 UP 主列表"""

        subs = Sub.all()
        uid_list['live']['list'] = list(set([sub.uid async for sub in subs
                                             if sub.live]))
        uid_list['dynamic']['list'] = list(set([sub.uid async for sub in subs
                                                if sub.dynamic]))

    @classmethod
    async def update_user(cls, uid: int, name: str) -> bool:
        """更新 UP 主信息"""

        return bool(await User.filter(Q(uid=uid)).update(name=name))

    async def update_version(self):
        """更新版本号"""

        if not await self._need_update():
            return
        
        logger.info("正在更新数据库")        
        DBVersion.all().update(version=__version__)
        logger.info(f"数据库已更新至 v{__version__}")

    async def migrate_from_json(self):
        """从 TinyDB 的 config.json 迁移数据"""

        if not Path(get_path('config.json')).exists():
            return
        
        logger.info("正在从 config.json 迁移数据库")
        with open(get_path('config.json'), 'r', encoding='utf-8') as f:
            old_db = json.loads(f.read())
        subs: Dict[int, Dict] = old_db['_default']
        groups: Dict[int, Dict] = old_db['groups']
        for sub in subs.values():
            await self.add_sub(
                uid = sub['uid'],
                type_ = sub['type'],
                type_id = sub['type_id'],
                bot_id = sub['bot_id'],
                name = sub['name'],
                live = sub['live'],
                dynamic = sub['dynamic'],
                at = sub['at']
            )
        for group in groups.values():
            await self.set_permission(group['group_id'], group['admin'])
        
        Path(get_path('config.json')).rename(get_path('config.json.bak'))
        logger.info("数据库迁移完成")

    async def backup(self):
        """备份数据库"""
        pass

    @classmethod
    async def get_login(cls):
        """获取登录信息"""
        pass

    @classmethod
    async def update_login(cls, tokens):
        """更新登录信息"""
        pass


async def init():
    async with DB() as db:
        await db.init()
        await db.update_version()
        await db.migrate_from_json()
        await db.update_uid_list()


get_driver().on_startup(init)
get_driver().on_shutdown(Tortoise.close_connections)
