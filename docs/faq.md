# 常见问题

[[toc]]

## 怎么更新 HarukaBot？

更新至最新稳定版（推荐）

:::: code-group
::: code-group-item pip

```sh
pip install --upgrade haruka-bot
```
:::

::: code-group-item poetry

```sh
poetry add haruka-bot@latest
```
:::
::::

更新至最新测试版

:::: code-group
::: code-group-item pip

```sh
pip install --upgrade --pre haruka-bot
```
:::

::: code-group-item poetry

```sh
poetry add --allow-prereleases haruka-bot@latest
```
:::
::::

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

## 启动的时候出现 pytz.exceptions.UnknownTimeZoneError: 'Can not find timezone '

- 请依次点开 控制面板 -> 时钟和区域 -> 更改时区，如果出现【无法识别你当前的时区，请选择一个有效的时区】，点击更改时区选择到你所在地区的对应时区，然后重启 go-cqhttp 和 HarukaBot。

- 如果本来就是正常时区，尝试切换一个别的时区再切回来。

## 推送失败、截图失败等

这些都是因为网络波动产生的问题，HarukaBot 会自动重试不影响推送。

如果该问题频繁出现请检查当前网络环境，如网络是否通畅，有没有与代理软件冲突。

## 机器人不发消息也没反应

1. 检查 HarukaBot 与 go-cqhttp 连接是否正确。正常情况下 HarukaBot 的日志框中会显示接收到的 QQ消息。

2. 新部署的 go-cqhttp 会被 tx 风控，部分乃至全部消息类型会被风控（带图、带链接、长文本等）。如果在 go-cqhttp 日志中理应发送消息的时间点看见了类似 `【疑似账号被风控】` 的字样，则确实被风控了。  
被风控的账号需要在当前环境中挂几天（约 3 ~ 7 天不等），方可正常推送。


## 日志中出现了 `api timeout`，且浏览器访问所有B站的用户主页均变为空白

HarukaBot 会保持一个尽可能高但是不会触发风控的频率抓取 B站 的 API 进行请求。  
如果你是在本地部署的 HarukaBot，那么你使用任何设备访问 B站 的行为，都可能因为超过频率上限而触发风控。触发风控后，当前网络半小时内无法访问 B站 对应的某个 API，这也是不建议在本地部署的原因（电脑24小时不关机也很费电费也是真的）。

## 如何部署到服务器上？

- 25岁以下可以购买阿里云或腾讯云的学生服务器，一般一年也就一百左右。

- 买完安装系统的时候选择 Windows Server，通过远程连接后，就会出现你熟悉的 Windows 界面了。

- 之后就跟本地部署一样啦。

## 监听反向 WS API 时出现错误

通常为启动 go-cqhttp 后没有及时启动 HarukaBot 导致。会在 HarukaBot 启动并连接成功后停止。

如果 HarukaBot 启动后报错仍未停止，请重新阅读文档，检查 go-cqhttp 的配置是否正确。

## 如何更新 go-cqhttp？

去 [这里](https://github.com/Mrs4s/go-cqhttp/releases) 下载最新的版本。
