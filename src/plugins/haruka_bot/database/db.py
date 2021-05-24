from typing import List
import nonebot

from nonebot.adapters.cqhttp.event import GroupMessageEvent, MessageEvent
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.query import Query

from .models import Base, Group, Sub, User
from ..utils import get_path


uid_list = {'live': {'list': [], 'index': 0},
            'dynamic': {'list': [], 'index': 0}}

class DB:
    """数据库交互类，与增删改查无关的部分不应该在这里面实现"""

    engine = create_engine(f"sqlite:///{get_path('data.db')}")
    Base.metadata.create_all(engine)
    Session= sessionmaker(bind=engine)

    async def __aenter__(self):
        self.session: Session = self.Session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.session.commit()
        self.session.close()

    async def add_group(self, group_id):
        """创建群设置"""

        if self.session.query(Group).filter(Group.id == group_id).first():
            # 权限开关已经创建过了
            return
        # TODO 自定义默认权限
        group = Group(id=group_id, admin=True)
        self.session.add(group)
        self.session.commit()

    async def add_sub(self, uid, type_, type_id, bot_id, name, live=True,
                      dynamic=True, at=False) -> bool:
        """添加订阅"""

        if await self.get_sub(uid, type_, type_id):
            return False
        if not await self.get_user(uid):
            await self.add_user(uid, name)
        if type_ == 'group':
            await self.add_group(type_id)
        sub = Sub(uid=uid,
                  type=type_,
                  type_id=type_id,
                  # TODO 自定义默认动态直播全体开关
                  live=live,
                  dynamic=dynamic,
                  at=at,
                  bot_id=bot_id)
        self.session.add(sub)
        await self.update_uid_list()
        self.session.commit()
        return True

    async def add_user(self, uid, name):
        """添加 UP 主信息"""

        user = User(uid=uid, name=name)
        self.session.add(user)
        self.session.commit()


    async def delete_group(self, group_id) -> bool:
        """删除群设置"""

        if await self.get_sub(type_='group', type_id=group_id):
            # 当前群还有订阅，不能删除
            return False

        query = self.session.query(Group).filter(Group.id == group_id)
        query.delete()
        self.session.commit()

    async def delete_sub(self, uid, type_, type_id) -> bool:
        """删除指定订阅"""

        if not await self.get_sub(uid, type_, type_id):
            # 订阅不存在
            return False
        query = await self.get_subs(uid, type_, type_id)
        query.delete()
        await self.delete_user(uid)
        await self.update_uid_list()
        self.session.commit()
        return True

    async def delete_sub_list(self, type_, type_id):
        "删除指定位置的推送列表"

        subs = await self.get_subs(type_=type_, type_id=type_id)
        uids = [sub.uid for sub in subs]
        subs.delete()
        self.session.commit()
        for uid in uids:
            await self.delete_user(uid)
        if type_ == 'group':
            await self.delete_group(type_id)

    async def delete_user(self, uid) -> bool:
        """删除 UP 主信息"""

        if await self.get_sub(uid):
            # 还存在该 UP 主订阅，不能删除
            return False
        query = self.session.query(User).filter(User.uid == uid)
        query.delete()
        self.session.commit()
        return True

    async def get_push_list(self, uid, func) -> List[Sub]:
        """根据类型和 UID 获取需要推送的 QQ 列表"""
        
        return (await self.get_subs(uid, **{func: True})).all()

    async def get_sub(self, uid, type_=None, type_id=None):
        """获取指定位置的订阅信息"""

        return (await self.get_subs(uid, type_, type_id)).first()

    async def get_sub_list(self, type_, type_id) -> List[Sub]:
        """获取指定位置的推送列表"""

        return (await self.get_subs(type_=type_, type_id=type_id)).all()

    async def get_subs(self, uid=None, type_=None, type_id=None, live=None,
                       dynamic=None, at=None, bot_id=None) -> Query:
        """获取指定的订阅数据"""

        kw = locals()
        del kw['self']
        kw['type'] = kw.pop('type_')
        filters = [getattr(Sub, key) == value for key, value in kw.items()
                   if value != None]
        return self.session.query(Sub).filter(*filters)

    async def get_uid_list(self, func) -> List:
        """根据类型获取需要爬取的 UID 列表"""
        
        return uid_list[func]['list']

    async def get_user(self, uid: int):
        """获取 UP 主信息，没有就返回 None"""

        return self.session.query(User).filter(User.uid == uid).first()

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

    async def set_permission(self, group_id, switch):
        """设置指定位置权限"""

        # TODO 重构为 set_group
        group = self.session.query(Group).filter(Group.id == group_id).first()
        group.admin = switch
        self.session.commit()

    async def set_sub(self, conf, switch, uid=None, type_=None, type_id=None):
        """开关订阅设置"""

        subs = await self.get_subs(uid, type_, type_id)
        if subs.count() == 0:
            return False
        for sub in subs:
            setattr(sub, conf, switch)
        self.session.commit()
        return True

    async def update_uid_list(self):
        """更新需要推送的 UP 主列表"""

        subs = self.session.query(Sub).all()
        uid_list['live']['list'] = list(set([sub.uid for sub in subs
                                             if sub.live]))
        uid_list['dynamic']['list'] = list(set([sub.uid for sub in subs
                                                if sub.dynamic]))

    @classmethod
    async def get_name(cls, uid):
        """根据 UID 获取缓存昵称"""
        pass

    @classmethod
    async def get_login(cls):
        """获取登录信息"""
        pass

    @classmethod
    async def update_login(cls, tokens):
        """更新登录信息"""
        pass

    async def new_version(self):
        """检查是否为最新版本"""
        pass

    async def update_version(self):
        """更新版本号"""
        pass

    @classmethod
    async def update_config(cls):
        """更新数据库"""
        pass

async def init_push_list():
    async with DB() as db:
        await db.update_uid_list()

nonebot.get_driver().on_startup(init_push_list)