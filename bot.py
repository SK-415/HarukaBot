#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
import os
from os import path
from nonebot.log import logger, default_format


logger.add(path.join('log', "error.log"),
           rotation="00:00",
           retention='1 week',
           diagnose=False,
           level="ERROR",
           format=default_format)

# You can pass some keyword args config to init function
nonebot.init()
app = nonebot.get_asgi()

nonebot.load_builtin_plugins()
nonebot.load_plugins("plugins")

# Modify some config / config depends on loaded configs
# 
# config = nonebot.get_driver().config
# do something...


if __name__ == "__main__":
    # 将工作目录切换到 bot.py 所在的文件夹
    os.chdir(path.dirname(path.abspath(__file__)))

    # 列出 \plugins 下所有的插件
    for dirname in os.listdir('plugins'):
        if dirname != '__pycache__' and path.isdir(path.join('plugins', dirname)):
            # 检查是否有对应 data 文件夹, 没有就创建一个
            if not path.isdir(path.join('data', dirname)):
                os.makedirs(path.join('data', dirname))

    nonebot.run(app="bot:app")
