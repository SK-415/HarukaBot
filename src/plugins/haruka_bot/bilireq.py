import asyncio
import base64
import io
import json
from logging import exception
import time
from hashlib import md5
from urllib.parse import urlencode

import httpx
import qrcode
from httpx import ConnectTimeout, ReadTimeout
from nonebot.log import logger

from .config import Config


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
        self.login = Config.get_login()
        self.proxies = {
            'http': None,
            'https': None
        }

    async def request(self, method, url, **kw):
        # TODO 处理 -412
        async with httpx.AsyncClient(proxies=self.proxies) as client:
            try:
                r = await client.request(method, url, **kw)
            except ConnectTimeout:
                logger.error(f"连接超时（{url}）")
                raise
            except ReadTimeout:
                logger.error(f"接收超时（{url}）")
                raise
            except exception as e:
                logger.error(f"未知错误（url）")
                raise 
        r.encoding = 'utf-8'
        return r
    
    async def get(self, url, **kw):
        return await self.request('GET', url, **kw)

    async def post(self, url, **kw):
        return await self.request('POST', url, **kw)
    
    async def get_info(self, uid):
        url = f'https://api.bilibili.com/x/space/acc/info?mid={uid}'
        return (await self.get(url, headers=self.default_headers)).json()['data']

    async def get_user_dynamics(self, uid):
        # need_top: {1: 带置顶, 0: 不带置顶}
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&offset_dynamic_id=0&need_top=0'
        return (await self.get(url, headers=self.default_headers)).json()['data']
    
    async def get_new_dynamics(self):
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new'
        params = {'type_list': 268435455, 'access_key': self.login['access_token']}
        return (await self.get(url, params=params)).json()['data']

    async def get_history_dynamics(self, offset_id):
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_history'
        params = {
            'type_list': 268435455,
            'access_key': self.login['access_token'],
            'offset_dynamic_id': offset_id
        }
        return (await self.get(url, params=params)).json()['data']
    
    async def get_live_list(self, uids):
        """根据 UID 获取直播间信息列表"""

        url = 'https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids'
        data = {'uids': uids}
        return (await self.post(url, headers=self.default_headers, data=json.dumps(data))).json()['data']
    
    async def get_is_live_list(self):
        url = 'https://api.live.bilibili.com/xlive/app-interface/v1/relation/liveAnchor'
        params = {'access_key': self.login['access_token']}
        return (await self.get(url, params=params)).json()['data']
    
    async def get_live_info(self, uid):
        url = f'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={uid}'
        return (await self.get(url, headers=self.default_headers)).json()['data']

    def _sign(self, params):
        """获取 params 的 sign 值"""

        items = sorted(params.items())
        return md5(
            f"{urlencode(items)}{self.appsec}".encode('utf-8')
            ).hexdigest()

    async def get_qr(self):
        """QR码 登录"""

        params = {
            'appkey': self.appkey,
            'local_id': 0,
            'ts': int(time.time())
        }
        params['sign'] = self._sign(params)
        url = "http://passport.bilibili.com/x/passport-tv-login/qrcode/auth_code"
        r = (await self.post(url, params=params)).json()
        self.auth_code = r['data']['auth_code']

        qr = qrcode.QRCode()
        qr.add_data(r['data']['url'])
        img = qr.make_image()
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        heximage = base64.b64encode(buf.getvalue())
        self.qr_img = heximage.decode()
        return self.qr_img

    async def qr_login(self):
        params = {
            'appkey': self.appkey,
            'local_id': 0,
            'auth_code': self.auth_code,
            'ts': int(time.time())
        }
        params['sign'] = self._sign(params)
        url = "http://passport.bilibili.com/x/passport-tv-login/qrcode/poll"
        while True:
            r = (await self.post(url, params=params)).json()
            code = r['code']
            if code == 0:
                tokens = r['data']
                Config.update_login(tokens)
                return "登入成功"
            elif code == 86038:
                return "二维码已失效，请重新登录"
            await asyncio.sleep(1)
