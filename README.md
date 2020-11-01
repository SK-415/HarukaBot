# HarukaBot

[![VERSION](https://img.shields.io/github/v/release/SK-415/HarukaBot)](https://github.com/SK-415/HarukaBot/releases)
[![time tracker](https://wakatime.com/badge/github/SK-415/HarukaBot.svg)](https://wakatime.com/badge/github/SK-415/HarukaBot)
[![STARS](https://img.shields.io/github/stars/SK-415/HarukaBot)](https://github.com/SK-415/HarukaBot/stargazers)
[![LICENSE](https://img.shields.io/github/license/SK-415/HarukaBot)](https://github.com/SK-415/HarukaBot/blob/master/LICENSE)

## 简介

一款将哔哩哔哩UP主的直播与动态信息推送至QQ的机器人. 基于 [`NoneBot2`](https://github.com/nonebot/nonebot2) 开发, 前身为 [`dd-bot`](https://github.com/SK-415/dd-bot) .

项目名称来源于B站 [@白神遥Haruka](https://space.bilibili.com/477332594)

HarukaBot 致力于为B站UP主们提供一个开源免费的粉丝群推送方案. 极大的减轻管理员负担, 不会再遇到突击无人推送的尴尬情况. 同时还能将B博动态截图转发至粉丝群, 活跃群内话题.

> 介于作者技术力低下, HarukaBot 的体验可能并不是很好. 如果使用中有任何意见或者建议都欢迎提出, 我会努力去完善它. 

## 功能介绍

HarukaBot 专注于订阅B站UP主们的动态与开播提醒, 并转发至QQ群/好友.

同时 HarukaBot 针对粉丝群中的推送场景进行了若干优化: 

- 权限开关: 指定某个群只有管理员才能触发指令

- @全体开关: 指定群里某位订阅的主播开播推送带@全体

- 动态/直播开关: 可以自由设置每位主播是否推送直播/动态

- 订阅列表: 每个群/好友的订阅都是分开来的

- 多端推送: 受限于一个QQ号一天只能@十次全体成员, 因此对于粉丝群多的UP来说一个 bot 的次数完全不够推送. 因此一台 HarukaBot 支持同时连接多个QQ, 分别向不同的群/好友同时推送

## 推送延迟

受限于B站对API爬取频率限制, 目前 HarukaBot 会将所有UP主排成一列, 每隔十秒检查一位. 因此如果 HarukaBot 订阅了 x 位UP主最高延迟就是 10x 秒.

虽然 HarukaBot 目前的推送延迟对于粉丝群来说是足够了, 但是很显然对于广大dd们来说并不友好, 随便订阅30+个主播延迟就能超过5分钟. 

目前 HarukaBot v1 的开发已接近尾声. v2 已在着手开发中, 将支持绑定B站id使用全新检测逻辑来大幅缩短推送延迟, 不再受限于订阅数量.

## 部署教程

文档撰写中ing...

## 支持作者

点个小星星就是对我最好的支持. 感谢使用 HarukaBot. 
