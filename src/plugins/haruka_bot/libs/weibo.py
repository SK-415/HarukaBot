from nonebot.adapters.cqhttp.message import MessageSegment
from dateutil import parser

class Weibo():
    def __init__(self, wb):
        self.weibo = wb
        self.id = wb['mblogid']
        self.uid = wb['user']['id']
        self.name = wb['user']['screen_name']
        self.url = f"https://weibo.com/{self.uid}/{self.id}"
        self.time = parser.parse(wb['created_at']).timestamp()

    async def format(self, img):
        self.message = (f"{self.name} " +
                        f"发布了新微博：\n" +
                        f"{self.url}\n" +
                        MessageSegment.image(f"base64://{img}")
                        )
