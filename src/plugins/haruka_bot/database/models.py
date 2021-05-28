from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Sub(Base):
    __tablename__ = "subs"

    type = Column(String(10), primary_key=True)
    type_id = Column(Integer(), primary_key=True)
    uid = Column(Integer(), primary_key=True)
    live = Column(Boolean())
    dynamic = Column(Boolean())
    at = Column(Boolean())
    bot_id = Column(Integer())


class User(Base):
    __tablename__ = "users"

    uid = Column(Integer(), primary_key=True)
    name = Column(String(20))


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer(), primary_key=True)
    admin = Column(Boolean())

class Version(Base):
    __tablename__ = "version"

    version = Column(String(30), primary_key=True)
