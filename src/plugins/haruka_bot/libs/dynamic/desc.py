from typing import Optional

from pydantic import BaseModel

from .user_profile import UserProfile


class Desc(BaseModel):
    type: int
    timestamp: int
    view: int
    orig_dy_id: Optional[int]
    orig_type: int
    user_profile: UserProfile
    dynamic_id: int
    # uid: int
    # rid: int
    # acl: int
    # repost: int
    # comment: int
    # like: int
    # is_liked: int
    # pre_dy_id: int
    # uid_type: int
    # stype: int
    # r_type: int
    # inner_id: int
    # status: int
    # dynamic_id_str: str
    # pre_dy_id_str: str
    # orig_dy_id_str: str
    # rid_str: str