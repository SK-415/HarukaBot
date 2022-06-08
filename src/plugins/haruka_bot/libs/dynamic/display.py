from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Json


class TopicDetail(BaseModel):
    topic_name: str
    is_activity: bool


class TopicInfo(BaseModel):
    topic_details: List[TopicDetail]


class EmojiDetail(BaseModel):
    emoji_name: str
    id: int
    text: str
    url: str


class EmojiInfo(BaseModel):
    """emoji 信息"""
    emoji_details: List[EmojiDetail]


class DescFirst(BaseModel):
    text: str


class ReserveAttachCard(BaseModel):
    title: Optional[str]
    desc_first: Optional[Union[str, DescFirst]]
    desc_second: Optional[str]
    cover_url: Optional[str]
    head_text: Optional[str]


class AddOnCardInfo(BaseModel):
    add_on_card_show_type: int
    reserve_attach_card: Optional[ReserveAttachCard]
    vote_card: Optional[Json]
    attach_card: Optional[ReserveAttachCard]


class Display(BaseModel):
    topic_info: Optional[TopicInfo]
    emoji_info: Optional[EmojiInfo]
    add_on_card_info: Optional[List[AddOnCardInfo]]
    origin: Optional[Dict]
