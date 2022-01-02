import json
from logging import exception
from hashlib import md5
from typing import Any, Dict
from urllib.parse import urlencode

import httpx
from httpx import ConnectTimeout, ReadTimeout, ConnectError
from nonebot.log import logger
from httpx._types import URLTypes


class RequestError(Exception):
    def __init__(self, code, message=None, data=None):
        self.code = code
        self.message = message
        self.data = data
    
    def __repr__(self):
        return f"<RequestError code={self.code} message={self.message}>"
    
    def __str__(self):
        return self.__repr__()


class BiliReq():
    def __init__(self):
        self.appkey = "4409e2ce8ffd12b8"
        self.appsec = "59b43e04ad6965f34319062b478f83dd"
        self.default_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
             AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88\
              Safari/537.36 Edg/87.0.664.60',
            'Referer': 'https://www.bilibili.com/'
        }
        # self.login = Config.get_login()
        self.proxies: Dict[URLTypes, Any] = {'all://': None}

    # TODO 制作一个装饰器捕获请求时的异常并用更友好的方式打印出来
    async def request(self, method, url, **kw) -> Dict:
        async with httpx.AsyncClient(proxies=self.proxies) as client:
            try:
                r = await client.request(method, url, **kw)
                r.encoding = 'utf-8'
                res: Dict = r.json()
            except ConnectTimeout:
                logger.error(f"连接超时（{url}）")
                raise
            except ReadTimeout:
                logger.error(f"接收超时（{url}）")
                raise
            except exception as e:
                logger.error(f"未知错误（url）")
                raise 
            
            if res['code'] != 0:
                raise RequestError(code=res['code'],
                                    message=res['message'],
                                    data=res.get('data'))
            return res['data']
    
    async def get(self, url, **kw):
        return await self.request('GET', url, **kw)

    async def post(self, url, **kw):
        return await self.request('POST', url, **kw)
    
    async def get_info(self, uid):
        url = f'https://api.bilibili.com/x/space/acc/info?mid={uid}'
        return await self.get(url, headers=self.default_headers)

    async def get_user_dynamics(self, uid):
        # need_top: {1: 带置顶, 0: 不带置顶}
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&offset_dynamic_id=0&need_top=0'
        return await self.get(url, headers=self.default_headers)
    
    # async def get_new_dynamics(self):
    #     url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new'
    #     params = {'type_list': 268435455, 'access_key': self.login['access_token']}
        return await self.get(url, params=params)

    # async def get_history_dynamics(self, offset_id):
    #     url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_history'
    #     params = {
    #         'type_list': 268435455,
    #         'access_key': self.login['access_token'],
    #         'offset_dynamic_id': offset_id
    #     }
    #     return await self.get(url, params=params)
    
    async def get_live_list(self, uids):
        """根据 UID 获取直播间信息列表"""

        url = 'https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids'
        data = {'uids': uids}
        return await self.post(url, headers=self.default_headers, data=json.dumps(data))
    
    # async def get_is_live_list(self):
    #     url = 'https://api.live.bilibili.com/xlive/app-interface/v1/relation/liveAnchor'
    #     params = {'access_key': self.login['access_token']}
    #     return await self.get(url, params=params)
    
    async def get_live_info(self, uid):
        url = f'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={uid}'
        return await self.get(url, headers=self.default_headers)

    def _sign(self, params):
        """获取 params 的 sign 值"""

        items = sorted(params.items())
        return md5(
            f"{urlencode(items)}{self.appsec}".encode('utf-8')
            ).hexdigest()


    async def get_uid_through_name(self,name):
        """根据 UP名称 获取搜索到的第一个用户的uid"""

        url = 'https://api.bilibili.com/x/web-interface/search/type'
        params = {
            'keyword':name,
            'search_type':'bili_user'
        }
        return await self.get(url, params=params)