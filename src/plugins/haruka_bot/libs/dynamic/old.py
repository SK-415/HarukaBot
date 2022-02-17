from nonebot.adapters.onebot.v11.message import MessageSegment


class Dynamic:
    def __init__(self, dynamic):
        # self.origin = json.loads(self.card['origin'])
        self.dynamic = dynamic
        # self.card = json.loads(dynamic['card'])
        # self.dynamic['card'] = self.card
        self.type = dynamic["desc"]["type"]
        self.id = dynamic["desc"]["dynamic_id"]
        self.url = "https://t.bilibili.com/" + str(self.id)
        self.time = dynamic["desc"]["timestamp"]
        # self.origin_id = dynamic['desc']['orig_dy_id']
        self.uid = dynamic["desc"]["user_profile"]["info"]["uid"]
        self.name = dynamic["desc"]["user_profile"]["info"].get("uname")
        # self.name = dynamic["desc"]["user_profile"]["info"].get(
        #     "uname", Config.get_name(self.uid)
        # )

    async def format(self, img):
        type_msg = {
            0: "发布了新动态",
            1: "转发了一条动态",
            8: "发布了新投稿",
            16: "发布了短视频",
            64: "发布了新专栏",
            256: "发布了新音频",
        }
        self.message = (
            f"{self.name} "
            + f"{type_msg.get(self.type, type_msg[0])}：\n"
            + f"{self.url}\n"
            + MessageSegment.image(f"base64://{img}")
        )
