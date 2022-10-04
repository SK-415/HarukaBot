from typing import List

from ..database.models import Sub, Guild
from ..database.db import DB as db


class DBGuild:
    @classmethod
    async def set_guild_permission(cls, guild_id, channel_id, switch):
        """设置指定频道权限"""
        result = await cls.get_guild(
            guild_id=guild_id,
            channel_id=channel_id,
        )
        if result:
            await Guild.update({"guild_id": guild_id, "channel_id": channel_id}, admin=switch)
        else:
            await cls.add_guild(
                guild_id=guild_id,
                channel_id=channel_id,
                admin=switch
            )

    @classmethod
    async def get_guild_sub_list(cls, type, guild_id, channel_id) -> List[Sub]:
        """获取指定位置的推送列表"""
        guild = await  cls.get_guild_db_id(guild_id=guild_id, channel_id=channel_id)
        return await db.get_subs(type=type, type_id=guild.id)

    @classmethod
    async def add_guild_sub(cls, *, name, guild_id, channel_id, **kwargs) -> bool:
        """添加订阅"""
        if not await Sub.add(**kwargs):
            return False
        await db.add_user(uid=kwargs["uid"], name=name)
        if kwargs["type"] == "guild":
            # 在guild表添加频道
            await cls.add_guild(
                guild_id=guild_id,
                channel_id=channel_id,
                admin=True,
            )

        await db.update_uid_list()
        return True

    @classmethod
    async def add_guild(cls, **kwargs):
        """创建频道设置"""
        return await Guild.add(**kwargs)

    @classmethod
    async def get_guild(cls, **kwargs):
        """获取频道设置"""
        return await Guild.get(**kwargs).first()

    @classmethod
    async def get_guild_db_id(cls, **kwargs):
        """获取频道表中排序ID"""
        guild = await cls.get_guild(
            guild_id=kwargs["guild_id"],
            channel_id=kwargs["channel_id"],
        )
        if guild:
            return guild
        else:
            await cls.add_guild(
                guild_id=kwargs["guild_id"],
                channel_id=kwargs["channel_id"],
                admin=True,
            )
        return await cls.get_guild(
            guild_id=kwargs["guild_id"],
            channel_id=kwargs["channel_id"],
        )

    @classmethod
    async def get_guild_id(cls, id):
        async for sub in Guild.get(id=id):
            guild = {
                "guild_id": sub.guild_id,
                "channel_id": sub.channel_id,

            }
        return guild

    @classmethod
    async def delete_guild_sub(cls, uid, type, type_id) -> bool:
        """删除指定订阅"""
        # 如果删除成功
        if await Sub.delete(uid=uid, type=type, type_id=type_id):
            # 删除该UP
            await db.delete_user(uid=uid)
            # 如果该子频道为空，则删除该子频道的记录
            await cls.delete_guild(id=type_id)
            await db.update_uid_list()
            return True
        # 订阅不存在
        return False

    @classmethod
    async def delete_guild(cls, id) -> bool:
        """删除子频道设置"""
        if await db.get_sub(type="guild", type_id=id):
            # 当前频道还有订阅，不能删除
            return False
        await Guild.delete(id=id)
        return True
