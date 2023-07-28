from bilireq.utils import get, DEFAULT_HEADERS

async def get_user_dynamics(
    uid: int, cookie: str, ua: str, **kwargs
):
    """根据 UID 批量获取直播间信息"""
    url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space"
    data = {"host_mid": uid}
    headers = {
        **DEFAULT_HEADERS,
        **{"Cookie":cookie,
           "User-Agent": ua,
           "Origin": "https://space.bilibili.com",
           "Referer": f"https://space.bilibili.com/{uid}/dynamic"}}
    return await get(url, params=data, headers=headers)