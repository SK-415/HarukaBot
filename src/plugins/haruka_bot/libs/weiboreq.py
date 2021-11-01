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


class WeiboReq():
    def __init__(self, cookie):
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30',
            'Cookie': cookie,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
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
                logger.error(f"未知错误（{url}）")
                raise

            if res['ok'] != 1:
                raise RequestError(code=res['ok'],
                                   message=r.text,
                                   data=res.get('data'))
            return res['data']

    async def get(self, url, **kw):
        return await self.request('GET', url, **kw)

    async def post(self, url, **kw):
        return await self.request('POST', url, **kw)

    async def get_user_weibo(self, uid):
        # feature: {0: 带置顶, 1: 不带置顶}
        url = f'https://weibo.com/ajax/statuses/mymblog?uid={uid}&page=1&feature=1'
        return await self.get(url, headers=self.default_headers)