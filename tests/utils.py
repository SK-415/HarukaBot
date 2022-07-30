from nonebot.adapters.onebot.v11 import Message, PrivateMessageEvent, GroupMessageEvent
from nonebot.adapters.onebot.v11.event import Sender


def fake_private_event(msg="") -> PrivateMessageEvent:
    return PrivateMessageEvent(
        time=0,
        self_id=114514,
        post_type="message",
        message_type="private",
        sub_type="friend",
        message_id=0,
        user_id=-1,
        message=Message(msg),
        raw_message=msg,
        font=0,
        sender=Sender(),
        to_me=True,
    )


def fake_group_event(msg=""):
    pass
