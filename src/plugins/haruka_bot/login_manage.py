from typing import Tuple
import httpx
import time
from hashlib import md5
from urllib.parse import urlencode
import base64
import rsa,asyncio,json
from .config import Config
 
class BiliApi():
    """
        :说明:

          实现与哔哩哔哩进行业务交互的对象

        """
    def __init__(self):
        self.url = [
            "https://passport.bilibili.com/api/oauth2/getKey",
            "https://passport.bilibili.com/api/oauth2/info",
            "https://passport.bilibili.com/api/v2/oauth2/refresh_token",
            "https://passport.bilibili.com/x/passport-tv-login/login",
            "https://passport.bilibili.com/api/oauth2/revoke",
            "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_history",
            "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new",
            ]
        self.default_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
             AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88\
              Safari/537.36 Edg/87.0.664.60',
            'Referer': 'https://www.bilibili.com/'
        }
        self.TV_APPKEY = "4409e2ce8ffd12b8"
        self.TV_APPSEC = "59b43e04ad6965f34319062b478f83dd"
        self.cookie = Config.get_login()

    async def request(self, method, url, **kw):
        '处理请求的，带错误处理'
        # TODO 处理 -412
        async with httpx.AsyncClient(trust_env=False) as client:
            try:
                r = await client.request(method, url, **kw)
            except ConnectTimeout:
                logger.error(f"连接超时（{url}）")
                raise
            except ReadTimeout:
                logger.error(f"接收超时（{url}）")
                raise
            except exception as e:
                logger.error(f"未知错误（{url}）")
                raise 
        r.encoding = 'utf-8'
        return r

    async def get(self, url, **kw):
        '封装的GET请求'
        return (await self.request('GET', url, **kw)).json()

    async def post(self, url, **kw):
        '封装的POST请求'
        return (await self.request('POST', url, **kw)).json()
    
    async def get_sign(self, params):
        '签名'
        items = sorted(params.items())
        return md5(f"{urlencode(items)}{self.TV_APPSEC}".encode('utf-8')).hexdigest()

    async def encrypt_pwd(self, pwd):
        '加密密码'
        params = {
            'appkey': self.TV_APPKEY,
            'ts': int(time.time())
        }
        params['sign'] = await self.get_sign(params)
        res = await self.post(self.url[0], params = params)
        hash_s, rsa_pub = res["data"]["hash"], res["data"]["key"]
        return base64.b64encode(
            rsa.encrypt(
                (hash_s + pwd).encode(),
                rsa.PublicKey.load_pkcs1_openssl_pem(
                    rsa_pub.encode("utf-8")),
            )).decode('ascii')

    async def dynamic_json_translate(self,res):
        '动态的解析分类器,输入返回的json'
        # 建立一个数组
        inofmation = []
        # 告诉下面分类器怎么分类
        typelist = {1:["content","转发了"],2:["description","发布了新动态"],4:["content","发布了新动态"]}
        update_type_list ={8:["title","发布了新投稿"],64:["title","发布了新专栏"],256: ["title","发布了新音频"],16: ["title","发布了短视频"]}
        # 遍历每一张cards
        try:
            for cards in res['data']['cards']:
                #建立一个字典，每次循环会自动清空
                data = {}
                # 拿要用的东西
                data['uid'] = cards['desc']['uid']
                data['uname'] = cards['desc']['user_profile']['info']['uname']
                data['dynamic_id'] = cards['desc']['dynamic_id']
                data['rid'] = cards['desc']['rid']
                data['type'] = cards['desc']['type']
                cardstype = cards['desc']['type']
                data['timestamp'] = cards['desc']['timestamp']
                # data['cards'] = cards['card']
                # 看类型下菜 转发 动态 图片动态
                if cardstype == 1 or cardstype == 2 or cardstype == 4:
                    data['type_message'] = typelist[cardstype][1]
                    data['message'] = json.loads(cards['card'])['item'][typelist[cardstype][0]]
                    if cardstype == 2:
                        pictureslist = []
                        for pictures in json.loads(cards['card'])['item']['pictures']:
                            pictureslist.append(pictures['img_src'])
                        data['pictures'] = pictureslist
                # 投稿视频 专栏 音频 短视频
                elif cardstype == 8 or cardstype == 64 or cardstype == 16 or cardstype == 256:
                    data['type_message'] = update_type_list[cardstype][1]
                    data['message'] = json.loads(cards['card'])[update_type_list[cardstype][0]]
                else:
                    # 不支持的就跳出，不拿数据
                    print(f"不支持{cardstype}")
                    continue
                # 如果是含有转发的拿下来转发的源信息
                if cardstype == 1:
                    origin = {}
                    origin['orig_dy_id'] = cards['desc']['orig_dy_id']
                    origin['orig_type'] = cards['desc']['orig_type']
                    data['origin'] = origin
                # 把组装好的字典装入数组
                inofmation.append(data)
            # 丢出去
            # 妈的千万别出bug，我不想改这个恶心玩意
            dynamic_list = {}
            try:
                dynamic_list['max_dynamic_id']  = res['data']['max_dynamic_id']
            except:
                pass
            dynamic_list['count'] = len(inofmation)
            dynamic_list['data'] = inofmation
            return dynamic_list
        except:
            dynamic_list = {}
            try:
                dynamic_list['max_dynamic_id']  = res['data']['max_dynamic_id']
            except:
                pass
            dynamic_list['count'] = 0
            dynamic_list['msg'] = "没有新动态"
            return dynamic_list


    async def login_info(self, ACCESS_TOKEN):
        """
        :说明:

          查看登录信息

        :参数:

          * ACCESS_TOKEN: 上报token

        :返回:
            'code': 状态码
            'mid': UID
            'access_token': 上报token
            'expires_in': token 的剩余有效期(秒数)
            'userid': userid
            'uname': 用户名
        """
        params = {
            'appkey': self.TV_APPKEY,
            'access_token': ACCESS_TOKEN
        }
        params['sign'] = await self.get_sign(params)
        res = await self.get(self.url[1], params = params)
        if res['code'] != 0:
            return {"code":res['code'], "message":res['message']}
        else:
            data = {}
            data['code'] = res['code']
            for key in res['data']:
                data[key] = res['data'][key]
            return data
    
    async def refresh_token(self, ACCESS_TOKEN, REFRESH_TOKEN):
        """
        :说明:

          获取新的 token (令牌)，同时获得满血 cookie

        :参数:

          * ACCESS_TOKEN: 上报token
          * REFRESH_TOKEN: 刷新token

        :返回:
            'code': 状态码
            'mid': UID
            'access_token': 新的上报token
            'refresh_token': 新的刷新token
            'expires_in': token 的剩余有效期(秒数)
            'bili_jct': bili_jct
            'DedeUserID': DedeUserID
            'DedeUserID__ckMd5': DedeUserID__ckMd5
            'sid': sid
            'SESSDATA': SESSDATA
            'cookie_expires_in': cookie 的到期时间(时间戳)

        :注意:
            cookie 的有效期 (时间戳) 与 token 的到期时间 (秒数) 单位不一样，但都是30天。

        """
        params = {
            'access_token': ACCESS_TOKEN,
            'appkey': self.TV_APPKEY,
            'refresh_token': REFRESH_TOKEN
        }
        params['sign'] = await self.get_sign(params)
        res = await self.post(self.url[2], params = params)
        if res['code'] != 0:
            return {"code":res['code'], "message":res['message']}
        else:
            # 这个返回的东西太多了，这里整理一下，新建一个 dict
            data = {}
            # 把状态码搬下来
            data['code'] = res['code']
            # 把 access_token 和 refresh_token 整出来
            for key in res['data']['token_info']:
                data[key] = res['data']['token_info'][key]
            # 把 cookie 整理出来
            for cookiesdict in res['data']['cookie_info']['cookies']:
                data[cookiesdict['name']] = cookiesdict['value']
                data['cookie_expires_in'] = cookiesdict['expires']
            return data


    async def pwd_login(self, username, password):
        """
        :说明:

          通过tv端api进行账号密码登录

        :参数:

          * username: 用户名
          * password: 密码

        :返回:
            'code': 状态码
            'mid': UID
            'access_token': 上报token
            'refresh_token': 刷新token
            'expires_in': token 的剩余有效期(秒数)

        """
        params = {
            'appkey': self.TV_APPKEY,
            'local_id': 0,
            'username': username,
            'password': await self.encrypt_pwd(password),
            'ts': int(time.time())
        }
        params['sign'] = await self.get_sign(params)
        res = await self.post(self.url[3], params = params)
        if res['code'] != 0:
            return {"code":res['code'], "message":res['message']}
        else:
            res['data']['code'] = res['code']
            return res['data']

    async def logout(self, ACCESS_TOKEN):
        """
        :说明:

          登出

        :参数:

          * access_key: 上报token

        :返回:
            'code': 状态码
            'ts': 时间戳
        """
        params = {
            'access_key': ACCESS_TOKEN,
            'appkey': self.TV_APPKEY
        }
        params['sign'] = await self.get_sign(params)
        return (await self.post(self.url[4], params = params))
    async def dynamic_history(self, dynamic_id):
        """
        :说明:

          获取指定 dynamic_id 后的历史动态，验证方式 cookie

        :参数:

          * offset_dynamic_id: 指定 dynamic_id
          * cookie：cookie
          * uid：uid
        :返回:
            返回一个包含动态信息的数组，元素为该动态有关信息的字典，最多20条
        """
        cookie = self.cookie
        uid = cookie['DedeUserID']
        params = {'uid':uid,'type_list':268435455,'offset_dynamic_id':dynamic_id}
        res = await self.get(self.url[5], params = params, cookies = cookie)
        if res['code'] != 0:
            return {"code":res['code'], "message":res['message']}
        else:
            res['data']['code'] = res['code']
            data = await self.dynamic_json_translate(res)
            return data
    async def dynamic_new(self, dynamic_id):
        """
        :说明:

          获取指定 dynamic_id 前的动态，验证方式 cookie

        :参数:

          * current_dynamic_id: 指定 dynamic_id
          * cookie：cookie
          * uid：uid
        :返回:
            返回一个包含动态信息的数组，元素为该动态有关信息的字典，最多20条
        """
        cookie = self.cookie
        uid = cookie['DedeUserID']
        params = {'uid':uid,'type_list':268435455,'current_dynamic_id':dynamic_id}
        res = await self.get(self.url[6], params = params, cookies = cookie, headers = self.default_headers)
        if res['code'] != 0:
            return {"code":res['code'], "message":res['message']}
        else:
            res['data']['code'] = res['code']
            data = await self.dynamic_json_translate(res)
            return data



if __name__ == "__main__":
    def main():
        result = BiliApi.dynamic_new(BiliApi())
        #执行协程函数创建的协程对象时，协程函数内部的代码不会被执行，必须通过事件循环
        loop = asyncio.get_event_loop()
        loop.run_until_complete(result)

    main()