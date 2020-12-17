import httpx

class BiliReq():
    def __init__(self):
        self.default_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
             AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88\
              Safari/537.36 Edg/87.0.664.60',
            'Referer': 'https://www.bilibili.com/'
        }
    
    async def get(self, url, headers=None, cookies=None):
        if not headers:
            headers = self.default_headers
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=headers, cookies=cookies)
        r.encoding = 'utf-8'
        return r

    async def post(self, url, headers=None, cookies=None, data=None):
        if not headers:
            headers = self.default_headers
        async with httpx.AsyncClient() as client:
            r = await client.post(url, headers=headers, 
                                  cookies=cookies, data=data)
        r.encoding = 'utf-8'
        return r
    
    