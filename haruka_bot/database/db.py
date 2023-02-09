import json
from pathlib import Path
from typing import Dict, List, Optional

from nonebot import get_driver
from nonebot.log import logger
from packaging.version import Version as version_parser
from tortoise import Tortoise
from tortoise.connection import connections

from ..utils import get_path
from ..version import VERSION as HBVERSION
from .models import Group, Guild, Sub, User, Version

uid_list = {"live": {"list": [], "index": 0}, "dynamic": {"list": [], "index": 0}}
dynamic_offset = {}


class DB:
    """数据库交互类，与增删改查无关的部分不应该在这里面实现"""

    @classmethod
    async def init(cls):
        """初始化数据库"""
        config = {
            "connections": {
                # "haruka_bot": {
                #     "engine": "tortoise.backends.sqlite",
                #     "credentials": {"file_path": get_path("data.sqlite3")},
                # },
                "haruka_bot": f"sqlite://{get_path('data.sqlite3')}"
            },
            "apps": {
                "haruka_bot_app": {
                    "models": ["haruka_bot.database.models"],
                    "default_connection": "haruka_bot",
                }
            },
        }

        await Tortoise.init(config)

        await Tortoise.generate_schemas()
        await cls.migrate()
        await cls.update_uid_list()

    @classmethod
    async def get_user(cls, **kwargs):
        """获取 UP 主信息"""
        return await User.get(**kwargs).first()

    @classmethod
    async def get_name(cls, uid) -> Optional[str]:
        """获取 UP 主昵称"""
        user = await cls.get_user(uid=uid)
        if user:
            return user.name
        return None

    @classmethod
    async def add_user(cls, **kwargs):
        """添加 UP 主信息"""
        return await User.add(**kwargs)

    @classmethod
    async def delete_user(cls, uid) -> bool:
        """删除 UP 主信息"""
        if await cls.get_sub(uid=uid):
            # 还存在该 UP 主订阅，不能删除
            return False
        await User.delete(uid=uid)
        return True

    @classmethod
    async def update_user(cls, uid: int, name: str) -> bool:
        """更新 UP 主信息"""
        if await cls.get_user(uid=uid):
            await User.update({"uid": uid}, name=name)
            return True
        return False

    @classmethod
    async def get_group(cls, **kwargs):
        """获取群设置"""
        return await Group.get(**kwargs).first()

    @classmethod
    async def get_group_admin(cls, group_id) -> bool:
        """获取指定群权限状态"""
        group = await cls.get_group(id=group_id)
        if not group:
            # TODO 自定义默认状态
            return True
        return bool(group.admin)

    @classmethod
    async def get_guild_admin(cls, guild_id, channel_id) -> bool:
        """获取指定频道权限状态"""
        guild = await cls.get_guild(guild_id=guild_id, channel_id=channel_id)
        if not guild:
            # TODO 自定义默认状态
            return True
        return bool(guild.admin)

    @classmethod
    async def add_group(cls, **kwargs):
        """创建群设置"""
        return await Group.add(**kwargs)

    @classmethod
    async def add_guild(cls, **kwargs):
        """创建频道设置"""
        return await Guild.add(**kwargs)

    @classmethod
    async def delete_guild(cls, id) -> bool:
        """删除子频道设置"""
        if await cls.get_sub(type="guild", type_id=id):
            # 当前频道还有订阅，不能删除
            return False
        await Guild.delete(id=id)
        return True

    @classmethod
    async def delete_group(cls, id) -> bool:
        """删除群设置"""
        if await cls.get_sub(type="group", type_id=id):
            # 当前群还有订阅，不能删除
            return False
        await Group.delete(id=id)
        return True

    @classmethod
    async def set_permission(cls, id, switch):
        """设置指定群组权限"""
        if not await cls.add_group(id=id, admin=switch):
            await Group.update({"id": id}, admin=switch)

    @classmethod
    async def set_guild_permission(cls, guild_id, channel_id, switch):
        """设置指定频道权限"""
        if not await cls.add_guild(
            guild_id=guild_id, channel_id=channel_id, admin=switch
        ):
            await Guild.update(
                {"guild_id": guild_id, "channel_id": channel_id}, admin=switch
            )

    @classmethod
    async def get_guild(cls, **kwargs):
        """获取频道设置"""
        return await Guild.get(**kwargs).first()

    @classmethod
    async def get_guild_type_id(cls, guild_id, channel_id) -> Optional[int]:
        """获取频道订阅 ID"""
        guild = await Guild.get(guild_id=guild_id, channel_id=channel_id).first()
        return guild.id if guild else None

    @classmethod
    async def get_sub(cls, **kwargs):
        """获取指定位置的订阅信息"""
        return await Sub.get(**kwargs).first()

    @classmethod
    async def get_subs(cls, **kwargs):
        return await Sub.get(**kwargs)

    @classmethod
    async def get_push_list(cls, uid, func) -> List[Sub]:
        """根据类型和 UID 获取需要推送的 QQ 列表"""
        return await cls.get_subs(uid=uid, **{func: True})

    @classmethod
    async def get_sub_list(cls, type, type_id) -> List[Sub]:
        """获取指定位置的推送列表"""
        return await cls.get_subs(type=type, type_id=type_id)

    @classmethod
    async def add_sub(cls, *, name, **kwargs) -> bool:
        """添加订阅"""
        if not await Sub.add(**kwargs):
            return False
        await cls.add_user(uid=kwargs["uid"], name=name)
        if kwargs["type"] == "group":
            await cls.add_group(id=kwargs["type_id"], admin=True)
        await cls.update_uid_list()
        return True

    @classmethod
    async def delete_sub(cls, uid, type, type_id) -> bool:
        """删除指定订阅"""
        if await Sub.delete(uid=uid, type=type, type_id=type_id):
            await cls.delete_user(uid=uid)
            await cls.update_uid_list()
            return True
        # 订阅不存在
        return False

    @classmethod
    async def delete_sub_list(cls, type, type_id):
        """删除指定位置的推送列表"""
        async for sub in Sub.get(type=type, type_id=type_id):
            await cls.delete_sub(uid=sub.uid, type=sub.type, type_id=sub.type_id)
        await cls.update_uid_list()

    @classmethod
    async def set_sub(cls, conf, switch, **kwargs):
        """开关订阅设置"""
        return await Sub.update(kwargs, **{conf: switch})

    @classmethod
    async def get_version(cls):
        """获取数据库版本"""
        version = await Version.first()
        return version_parser(version.version) if version else None

    @classmethod
    async def migrate(cls):
        """迁移数据库"""
        DBVERSION = await cls.get_version()
        # 新数据库
        if not DBVERSION:
            # 检查是否有旧的 json 数据库需要迁移
            await cls.migrate_from_json()
            await Version.add(version=str(HBVERSION))
            return
        if DBVERSION != HBVERSION:
            # await cls._migrate()
            await Version.update({}, version=HBVERSION)
            return

    @classmethod
    async def migrate_from_json(cls):
        """从 TinyDB 的 config.json 迁移数据"""
        json_path = Path(get_path("config.json"))
        if not json_path.exists():
            return

        logger.info("正在从 config.json 迁移数据库")
        with json_path.open("r", encoding="utf-8") as f:
            old_db = json.loads(f.read())
        subs: Dict[int, Dict] = old_db["_default"]
        groups: Dict[int, Dict] = old_db["groups"]
        for sub in subs.values():
            await cls.add_sub(
                uid=sub["uid"],
                type=sub["type"],
                type_id=sub["type_id"],
                bot_id=sub["bot_id"],
                name=sub["name"],
                live=sub["live"],
                dynamic=sub["dynamic"],
                at=sub["at"],
            )
        for group in groups.values():
            await cls.set_permission(group["group_id"], group["admin"])

        json_path.rename(get_path("config.json.bak"))
        logger.info("数据库迁移完成")

    @classmethod
    async def get_uid_list(cls, func) -> List:
        """根据类型获取需要爬取的 UID 列表"""
        return uid_list[func]["list"]

    @classmethod
    async def next_uid(cls, func):
        """获取下一个要爬取的 UID"""
        func = uid_list[func]
        if func["list"] == []:
            return None

        if func["index"] >= len(func["list"]):
            func["index"] = 1
            return func["list"][0]
        else:
            index = func["index"]
            func["index"] += 1
            return func["list"][index]

    @classmethod
    async def update_uid_list(cls):
        """更新需要推送的 UP 主列表"""
        subs = Sub.all()
        uid_list["live"]["list"] = list(
            set([sub.uid async for sub in subs if sub.live])
        )
        uid_list["dynamic"]["list"] = list(
            set([sub.uid async for sub in subs if sub.dynamic])
        )

        # 清除没有订阅的 offset
        dynamic_offset_keys = set(dynamic_offset)
        dynamic_uids = set(uid_list["dynamic"]["list"])
        for uid in dynamic_offset_keys - dynamic_uids:
            del dynamic_offset[uid]
        for uid in dynamic_uids - dynamic_offset_keys:
            dynamic_offset[uid] = -1

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


get_driver().on_startup(DB.init)
get_driver().on_shutdown(connections.close_all)
