from tortoise.fields.data import BooleanField, CharField, IntField, TextField
from tortoise.models import Model


class BaseModel(Model):
    @classmethod
    def get_(cls, *args, **kwargs):
        super().get(*args, **kwargs)

    @classmethod
    def get(cls, **kwargs):
        return cls.filter(**kwargs)

    @classmethod
    async def add(cls, **kwargs):
        pk_name = cls.describe()["pk_field"]["name"]
        if pk_name == "id" and pk_name not in kwargs:
            filters = kwargs
        else:
            filters = {pk_name: kwargs[pk_name]}
        if await cls.get(**filters).exists():
            return False
        await cls.create(**kwargs)
        return True

    @classmethod
    async def delete(cls, **kwargs):
        query = cls.get(**kwargs)
        if await query.exists():
            await query.delete()
            return True
        return False

    @classmethod
    async def update(cls, q, **kwargs):
        query = cls.get(**q)
        if await query.exists():
            await query.update(**kwargs)
            return True
        return False

    class Meta:
        abstract = True


# TODO 自定义默认权限
class Sub(BaseModel):
    type = CharField(max_length=10)
    type_id = IntField()
    uid = IntField()
    live = BooleanField()  # default=True
    dynamic = BooleanField()  # default=True
    at = BooleanField()  # default=False
    bot_id = IntField()


class User(BaseModel):
    uid = IntField(pk=True)
    name = CharField(max_length=20)


class Group(BaseModel):
    id = IntField(pk=True)
    admin = BooleanField()  # default=True


class Guild(BaseModel):
    id = IntField(pk=True)
    guild_id = TextField()
    channel_id = TextField()
    admin = BooleanField()  # default=True


class Version(BaseModel):
    version = CharField(max_length=30)


# class Login(BaseModel):
#     uid = IntField(pk=True)
#     data = JSONField()
#     expireed = IntField()
