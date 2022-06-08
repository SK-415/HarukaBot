from typing import Optional

from pydantic import BaseModel


class Info(BaseModel):
    """用户信息"""
    uid: Optional[int]
    uname: Optional[str]
    face: Optional[str]
    head_url: Optional[str]
    name: Optional[str]


class LevelInfo(BaseModel):
    """等级信息"""
    current_level: Optional[int]


class Pendant(BaseModel):
    """挂件"""
    pid: int
    name: str
    image: str


class OfficialVerify(BaseModel):
    """账号认证信息"""
    type: int
    desc: str


class Card(BaseModel):
    official_verify: OfficialVerify


class VIP(BaseModel):
    """大会员信息"""
    vipType: int
    nickname_color: str


class UserProfile(BaseModel):
    info: Info
    level_info: Optional[LevelInfo]
    pendant: Optional[Pendant]
    card: Optional[Card]
    vip: Optional[VIP]