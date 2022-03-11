from typing import List, Optional, Union

from pydantic import BaseModel, Json

from .user_profile import UserProfile, Info


class Picture(BaseModel):
    img_src: str
    img_height: int
    img_width: int


class Item(BaseModel):
    at_control: Optional[Union[Json, str]]
    description: Optional[str]
    upload_time: Optional[int]
    content: Optional[str]
    ctrl: Optional[Union[Json, str]]
    pictures: Optional[Union[str, List[Picture]]]


class Vest(BaseModel):
    content: str


class APISeasonInfo(BaseModel):
    title: Optional[str]
    type_name: str


class Card(BaseModel):
    item: Optional[Item]
    dynamic: Optional[str]
    pic: Optional[str]
    title: Optional[str]
    origin: Optional[Json]
    image_urls: Optional[List]
    summary: Optional[str]
    vest: Optional[Vest]
    origin_user: Optional[UserProfile]

    duration: Optional[int]

    user: Optional[Info]
    owner: Optional[Info]
    author: Optional[Info]

    cover: Optional[str]
    area_v2_name: Optional[str]

    apiSeasonInfo: Optional[APISeasonInfo]

    new_desc: Optional[str]