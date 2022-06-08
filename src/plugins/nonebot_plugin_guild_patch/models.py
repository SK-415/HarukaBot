from typing import List, Optional, Type, TypeVar

from nonebot.adapters.onebot.v11 import (
    Adapter,
    Event,
    Message,
    MessageEvent,
    NoticeEvent,
)
from nonebot.log import logger
from pydantic import BaseModel, Field, parse_obj_as, validator
from typing_extensions import Literal

Event_T = TypeVar("Event_T", bound=Type[Event])


def register_event(event: Event_T) -> Event_T:
    Adapter.add_custom_model(event)
    logger.opt(colors=True).trace(
        f"Custom event <e>{event.__event__!r}</e> registered "
        f"from class <g>{event.__qualname__!r}</g>"
    )
    return event


@register_event
class GuildMessageEvent(MessageEvent):
    __event__ = "message.guild"
    self_tiny_id: int

    message_type: Literal["guild"]
    message_id: str
    guild_id: int
    channel_id: int

    raw_message: str = Field(alias="message")
    font: None = None

    @validator("raw_message", pre=True)
    def _validate_raw_message(cls, raw_message):
        if isinstance(raw_message, str):
            return raw_message
        elif isinstance(raw_message, list):
            return str(parse_obj_as(Message, raw_message))
        raise ValueError("unknown raw message type")


class ReactionInfo(BaseModel):
    emoji_id: str
    emoji_index: int
    emoji_type: int
    emoji_name: str
    count: int
    clicked: bool

    class Config:
        extra = "allow"


@register_event
class ChannelNoticeEvent(NoticeEvent):
    __event__ = "notice.channel"
    self_tiny_id: int
    guild_id: int
    channel_id: int
    user_id: int

    sub_type: None = None


@register_event
class MessageReactionUpdatedNoticeEvent(ChannelNoticeEvent):
    __event__ = "notice.message_reactions_updated"
    notice_type: Literal["message_reactions_updated"]
    message_id: str
    current_reactions: Optional[List[ReactionInfo]] = None


class SlowModeInfo(BaseModel):
    slow_mode_key: int
    slow_mode_text: str
    speak_frequency: int
    slow_mode_circle: int

    class Config:
        extra = "allow"


class ChannelInfo(BaseModel):
    owner_guild_id: int
    channel_id: int
    channel_type: int
    channel_name: str
    create_time: int
    creator_id: int
    creator_tiny_id: int
    talk_permission: int
    visible_type: int
    current_slow_mode: int
    slow_modes: List[SlowModeInfo] = []

    class Config:
        extra = "allow"


@register_event
class ChannelUpdatedNoticeEvent(ChannelNoticeEvent):
    __event__ = "notice.channel_updated"
    notice_type: Literal["channel_updated"]
    operator_id: int
    old_info: ChannelInfo
    new_info: ChannelInfo


@register_event
class ChannelCreatedNoticeEvent(ChannelNoticeEvent):
    __event__ = "notice.channel_created"
    notice_type: Literal["channel_created"]
    operator_id: int
    channel_info: ChannelInfo


@register_event
class ChannelDestroyedNoticeEvent(ChannelNoticeEvent):
    __event__ = "notice.channel_destroyed"
    notice_type: Literal["channel_destroyed"]
    operator_id: int
    channel_info: ChannelInfo
