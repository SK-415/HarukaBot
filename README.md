  
  
<p align="center">
  <img src="logo.png" width="200" height="200">
</p>
  
<h1 align="center">HarukaBot</h1>
<p align="center">
  <a href="https://github.com/SK-415/HarukaBot/releases">
    <img src="https://img.shields.io/github/v/release/SK-415/HarukaBot" alt="VERSION">
  </a>
  <a href="https://wakatime.com/badge/github/SK-415/HarukaBot">
    <img src="https://wakatime.com/badge/github/SK-415/HarukaBot.svg" alt="time tracker">
  </a>
  <a href="https://github.com/SK-415/HarukaBot/stargazers">
    <img src="https://img.shields.io/github/stars/SK-415/HarukaBot" alt="STARS">
  <a href="https://github.com/SK-415/HarukaBot/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/SK-415/HarukaBot" alt="LICENSE">
  </a>
  
##  目录
  
  
- [简介](#简介 )
- [功能介绍](#功能介绍 )
- [已知问题](#已知问题 )
  - [推送延迟](#推送延迟 )
  - [动态推送失效](#动态推送失效 )
- [部署指南](#部署指南 )
  - [部署 go-cqhttp](#部署-go-cqhttp )
  - [部署 HarukaBot](#部署-harukabot )
    - [方法一 懒人包 (部署方便无需依赖)](#方法一-懒人包-部署方便无需依赖 )
    - [方法二 手动安装 (较为复杂全平台通用)](#方法二-手动安装-较为复杂全平台通用 )
- [支持作者](#支持作者 )
  
##  简介
  
  
一款将哔哩哔哩UP主的直播与动态信息推送至QQ的机器人. 基于 [`NoneBot2`](https://github.com/nonebot/nonebot2 ) 开发, 前身为 [`dd-bot`](https://github.com/SK-415/dd-bot ) .
  
项目名称来源于B站 [@白神遥Haruka](https://space.bilibili.com/477332594 )
  
HarukaBot 致力于为B站UP主们提供一个开源免费的粉丝群推送方案. 极大的减轻管理员负担, 不会再遇到突击无人推送的尴尬情况. 同时还能将B博动态截图转发至粉丝群, 活跃群内话题.
  
> 介于作者技术力低下, HarukaBot 的体验可能并不是很好. 如果使用中有任何意见或者建议都欢迎提出, 我会努力去完善它. 
  
##  功能介绍
  
  
HarukaBot 专注于订阅B站UP主们的动态与开播提醒, 并转发至QQ群/好友.
  
同时 HarukaBot 针对粉丝群中的推送场景进行了若干优化: 
  
- **权限开关**: 指定某个群只有管理员才能触发指令
  
- **@全体开关**: 指定群里某位订阅的主播开播推送带@全体
  
- **动态/直播开关**: 可以自由设置每位主播是否推送直播/动态
  
- **订阅列表**: 每个群/好友的订阅都是分开来的
  
- **多端推送**: 受限于一个QQ号一天只能@十次全体成员, 因此对于粉丝群多的UP来说一个 bot 的次数完全不够推送. 因此一台 HarukaBot 支持同时连接多个QQ, 分别向不同的群/好友同时推送
  
##  已知问题
  
  
###  推送延迟
  
  
受限于B站对API爬取频率限制, 目前 HarukaBot 会将所有UP主排成一列, 每隔十秒检查一位. 因此如果 HarukaBot 订阅了 x 位UP主最高延迟就是 10x 秒.
  
> 虽然 HarukaBot 目前的推送延迟对于粉丝群来说是足够了, 但是很显然对于广大dd们来说并不友好, 随便订阅30+个主播延迟就能超过5分钟. 
> 因此, 未来的 HarukaBot v2 版中计划支持绑定B站账号, 将摆脱订阅数量越多推送越慢的窘境.
  
###  动态推送失效
  
  
在早晨约两点到八点期间, 部分服务器出现动态获取 api 失效的现象, 具体原因不明, 预计在 v2 中通过登录改善.
  
##  部署指南
  
  
**只有同时启动 go-cqhttp 和 HarukaBot 机器人才能正常运行.**
  
###  部署 go-cqhttp
  
  
1. 下载 [`go-cqhttp`](https://github.com/Mrs4s/go-cqhttp/releases ) (Windows 用户选择 `windows-amd64.zip` 结尾).
  
2. 解压至一个空文件夹后, 双击启动, 此时文件夹内会生成一个 `config.json` 文件, 打开并编辑. 
以下折叠部分为参考 (中文部分记得替换): 
  
<details>
<summary>config.json 设置参考</summary>
  
```json
{
	"uin": 机器人QQ号,
	"password": "QQ密码",
	"encrypt_password": false,
	"password_encrypted": "",
	"enable_db": true,
	"access_token": "",
	"relogin": {
		"enabled": true,
		"relogin_delay": 3,
		"max_relogin_times": 0
	},
	"_rate_limit": {
		"enabled": false,
		"frequency": 1,
		"bucket_size": 1
	},
	"ignore_invalid_cqcode": false,
	"force_fragmented": false,
	"heartbeat_interval": 0,
	"http_config": {
		"enabled": false,
		"host": "0.0.0.0",
		"port": 5700,
		"timeout": 0,
		"post_urls": {}
	},
	"ws_config": {
		"enabled": false,
		"host": "0.0.0.0",
		"port": 6700
	},
	"ws_reverse_servers": [
		{
			"enabled": true,
			"reverse_url": "ws://127.0.0.1:8080/cqhttp/ws",
			"reverse_api_url": "",
			"reverse_event_url": "",
			"reverse_reconnect_interval": 3000
		}
	],
	"post_message_format": "string",
	"debug": false,
	"log_level": "",
	"web_ui": {
		"enabled": false,
		"host": "127.0.0.1",
		"web_ui_port": 9999,
		"web_input": false
	}
}
```
</details>
  
</br>
  
3. 编辑完重启 `go-cqhttp.exe`, 跟着提示完成安全验证即可
  
###  部署 HarukaBot
  
  
####  方法一 懒人包 (部署方便无需依赖)
  
  
1. 下载[懒人包](https://github.com/SK-415/HarukaBot/releases ), 解压到任意位置.
  
2. 编辑 `env.prod` 文件, 将主人QQ号添加至 *SUPERUSERS*, 例: `SUPERUSERS=[123456]`
  
3. 双击 `bot.exe` 启动
  
####  方法二 手动安装 (较为复杂全平台通用)
  
  
1. 安装 [Python3.7+](https://www.python.org/downloads/release/python-386/ ) (安装的时候一定要[**勾选 "Add Python 3.x to PATH"**](https://www.liaoxuefeng.com/wiki/1016959663602400/1016959856222624 ) )
  
2. 克隆 or [下载](https://github.com/SK-415/HarukaBot/releases ) HarukaBot 源码到本地
  
3. 在源码根目录打开命令提示符 (对着文件夹内, 按住 shift 同时鼠标右键 -> 在此处打开 Powershell 窗口)
  
3. 输入 `pip install -r requirements.txt` 安装依赖
  
4. 输入 `python bot.py` 启动 HarukaBot
  
> 以后每次启动只需重复 3, 5 步骤
  
##  支持作者
  
  
点个小星星就是对我最好的支持. 感谢使用 HarukaBot. 也欢迎有能man对本项目pr.
  