# 常见问题

## 怎么更新 HarukaBot？

更新至最新稳定版（推荐）

<code-group>
<code-block title="pip">

```sh
pip install --upgrade haruka-bot
```
</code-block>

<code-block title="poetry">

```sh
poetry add haruka-bot@latest
```
</code-block>
</code-group>

更新至最新测试版

<code-group>
<code-block title="pip">

```sh
pip install --upgrade --pre haruka-bot
```
</code-block>

<code-block title="poetry">

```sh
poetry add --allow-prereleases haruka-bot@latest
```
</code-block>
</code-group>

## 如何查看别人的 UID？

::: warning 注意
UID 不是 直播间ID！  
UID 不是 直播间ID！  
UID 不是 直播间ID！
:::

### 网页端

- 点击头像进入他/她的个人空间。

- 查看网址，`space.bilibili.com/` 后面的那串数字就是 UID。

- 假设网址为 `https://space.bilibili.com/477332594/dynamic`，那么 UID 就是 `477332594`。

### 移动端

- 点击头像进入他/她的个人空间。

- 在个人签名处最右侧点击**详情**查看。

:::tip
如果你仍然无法找到 UID，可以点击 [这里](http://wbnbd.com/?q=%E5%A6%82%E4%BD%95%E6%9F%A5%E7%9C%8B%E5%88%AB%E4%BA%BA%E7%9A%84B%E7%AB%99UID) 获取更多信息   。
:::

### 启动方式

- 在配置完成后，建议先启动cqhttp，再通过对应方式启动harukabot

### 在hb启动中出现报错pytz.exceptions.UnknownTimeZoneError: 'Can not find timezone '

- 请依次点开 控制面板 -> 时钟和区域 -> 更改时区，如果出现【无法识别你当前的时区，请选择一个有效的时区】，点击更改时区选择到你所在地区的对应时区，然后重启cq和hb

- 附：已知V2ray会触发此问题，有条件请更换clash

- 如果本来就是正常时区，尝试切换一个别的时区再切回来

### 满屏都是红色的网络相关报错

- 代理软件请不要全局，开分流进行，以及并不建议将hb在本地部署，建议部署在云服务器上

### 机器人在群里发送【已检测到推送出现异常...】甚至可能一天在不同的群轮着发

- 大概率腾讯风控，请先考虑更换设备协议并开启fixurl，并检查cqhttp日志中对应时间是否存在【疑似账号被风控】字样

- 最速解决办法为直接给机器人开一个月SVIP，慢速解决办法为电脑和手机多挂一会，具体挂多久看脸。

### hb日志中出现pyppeteer.errors.TimeoutError: Navigation Timeout Exceeded: 30000 ms exceeded.

- 网络问题，或者当时网络存在波动，通常检查网络或者重启都能解决

### 在本地部署时，日志中出现了api timeout，且打开浏览器所有B站的用户主页均变为空白，但是视频和直播观看观看不受影响

- 对于hb来说，抓取B站api监控开播已经达到了尽可能最大且不触发风控的频率，如果在此基础上还进行频繁的api调取工作，会触发B站的api风控，半小时内所有的api请求都会无效，这也是不建议在本地部署的原因（电脑24小时不关机也很费电费也是真的）

### 我是小白，没有什么编程基础，如何将机器人搭载到服务器上？

- 云服务器通常就阿里云或者腾讯云，初次买一年的都很便宜。

- 买完在部署方面选择windows server 2007，通过远程连接后你会发现这就是个搭载在服务器上的win10

- 剩下的就是和本地一样的部署环节了。

### 有时候会出现同一个人的开播信息分成三次发出去，通常表现为【xxx开播啦】【直播封面图】【直播间链接】，或者会出现发出来的直播间链接或者动态链接中间会插入一个网址识别符号导致链接被切成两半，直接点是打不开链接的![11](https://user-images.githubusercontent.com/41290287/110202808-ffb9c380-7ea5-11eb-9467-5a5a2f2a3ba4.png)

- 此情况为fix_url功能导致，在cq后续版本中有修复，但仍有小概率复现（链接切开就是fixurl干的，只要开了就会切），理论上不属于hb解决范畴，可以尝试关闭fixurl，后续hb可能会尝试添加一个是否要发链接的开关

### hb报错：failed to handle event，结尾为1 validation error for event

- 如果机器人表现无异常可忽略，不会影响功能运行

### 监听反向WS API时出现错误

- 如果手速不够快 在先开cq时候没有及时打开hb，会出现此情况

- 在没有打开hb的情况下会反复报这个错误，在打开hb后会停止，hb打开后若停止报错为正常启动成功，可以忽略

- 如果hb打开之后仍然报错，请联系cq开发者获取更多帮助

### 同一个主播的开播提醒，有的群发的出来有的群发不出来，或者发出来了手机端看的到电脑端看不到。

- 请先检查机器人是否有管理员权限

- 如果没有管理员权限且确实无法沟通获得机器人的管理权限，可以关闭对应群的@全体成员

- 如果问题依旧，为触发了腾讯的隐性风控，暂无明确解决方案。

### 在正常没有问题的情况下，cq和hb的日志是什么样的

- cq和nb日志会有机器人所在群里的聊天消息，私聊的也有。

- 在触发对应需要机器人发消息的事件【比如开播，或指令】，cq会有日志写明消息发送到了哪里

- nb日志较为复杂且在群里有人发图片的时候会有很长的图片代码，不是很好找。

### 我该如何更新cq

- cq更新会发布在github：https://github.com/Mrs4s/go-cqhttp/releases 里面有详细的更新日志
