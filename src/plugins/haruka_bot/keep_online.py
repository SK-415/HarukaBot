# 这个啊，这个是监测哔哩哔哩token是否有效的定时任务。
from nonebot import require
from nonebot.log import logger
from .utils import scheduler
import asyncio,json,httpx
from .config import Config
from .login_manage import BiliApi
st = 0
# minute='*/30'
@scheduler.scheduled_job('cron', second='*/40', id='bilibili_on')
async def bilibili_online():
    'B站账号cookie有效性监测'
    password = "你的密码"
    loginname = "你的账号"
    b = BiliApi()
    with Config() as config:
        cookie = config.get_login()
        if cookie:
            data = await b.login_info(cookie['access_token'])
            if data['code'] == 0:
                if data['expires_in'] < 86400*7:
                    logger.debug(f"B站账号有效期小于7天，正在刷新token")
                    cookies = await b.refresh_token(cookie['access_token'], cookie['refresh_token'])
                    if cookies['code'] != 0:
                        logger.error(f"尝试失败!错误是：{data['cookies']}")
                    config.update_login(cookies)
                logger.debug(f"B站账号验证成功！欢迎{data['uname']},有效期剩余{data['expires_in']}")
            else:
                logger.error(f"B站账号验证失败！错误是：{data['message']}")
                logger.warning(f"B站账号验证失败！正在进行第{st}次重试")
                data = await b.pwd_login(loginname, password)
                if data['code'] != 0:
                    st =st + 1
                    logger.error(f"第{st}次尝试重新登录失败!错误是：{data['message']}")
                else:
                    cookies = await b.refresh_token(data['access_token'], data['refresh_token'])
                    config.update_login(cookies)
                    logger.info(f"重新登录成功")
        else:
            logger.info(f"登录")
            data = await b.pwd_login(loginname, password)
            if data['code'] != 0:
                st =st + 1
                logger.error(f"登录失败!错误是：{data['message']}")
            else:
                cookies = await b.refresh_token(data['access_token'], data['refresh_token'])
                config.update_login(cookies)
                logger.info(f"登录成功")
