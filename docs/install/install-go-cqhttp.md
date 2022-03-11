# 安装 go-cqhttp

::: danger 为什么需要 go-cqhttp？
HarukaBot 本身只负责处理 B 站信息，需要借助 go-cqhttp 与 QQ 进行通信。

同时 HarukaBot 仅使用 go-cqhttp 进行测试。使用其他 OneBot 实现（如 [OneBot Kotlin](https://github.com/yyuueexxiinngg/onebot-kotlin)），请**自行承担**可能存在的**兼容性问题**。
:::

::: tip 准备工作
- 一台服务器或能 24 小时运行的电脑
- 熟悉电脑基本操作（下载操作文件、安装卸载软件、使用命令行工具如 PowerShell 和 Bash）
:::

1. 下载最新版 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp/releases/latest)，不知道下哪个请参考 [版本说明](https://docs.go-cqhttp.org/guide/quick_start.html#%E4%B8%8B%E8%BD%BD)。

2. 创建一个空文件夹存放数据，并将解压好的 `go-cqhttp` 可执行文件放入其中。

3. 在当前文件夹内打开一个终端，并运行 `go-cqhttp`，选择 `3` 反向 Websocket 通信，在文件夹内生成 `config.yml` 配置文件。

4. 打开 `config.yml`，将下方示例内容覆盖或者对照修改原本内容，注意把 `uin` 改为自己机器人 QQ 号。

::: warning Windows 用户不要用记事本修改 config.yml
Windows 自带记事本可能导致文本乱码，请使用第三方文本编辑器，如 [NotePad3](https://www.rizonesoft.com/downloads/notepad3/)，[VS Code](https://code.visualstudio.com/Download)，[Sublime Text](http://www.sublimetext.com/3)。
:::

**示例版本：v1.0.0-beta8-fix2**


```yml
account:
  uin: 1233456 # 机器人QQ账号

servers:
  - ws-reverse:
      universal: ws://127.0.0.1:8080/onebot/v11/ws
```

5. 在终端中重新运行 `go-cqhttp`，跟随提示完成扫码登录和安全验证。
