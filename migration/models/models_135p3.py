from tortoise.models import Model
from tortoise.fields.data import CharField, IntField, BooleanField


class Sub(Model):
    type = CharField(max_length=10)
    type_id = IntField()
    uid = IntField()
    live = BooleanField()
    dynamic = BooleanField()
    at = BooleanField()
    bot_id = IntField()


class User(Model):
    uid = IntField(pk=True)
    name = CharField(max_length=20)


class Group(Model):
    id = IntField(pk=True)
    admin = BooleanField()


class Version(Model):
    version = CharField(max_length=30)
