# 安装 go-cqhttp

::: warning 注意
HarukaBot 一直是使用 go-cqhttp 进行开发的，同时适配了部分 go-cqhttp 非 OneBot 标准 API。

因此，**非常不建议**使用其他的 cqhttp 实现来代替 go-cqhttp，除非你愿意承担**兼容性问题**引发的**后果**。
:::

1. 下载自己系统对应的 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp/releases/latest) 版本。

::: tip 提示
文件名中包含 `amd64` 为 64位 版，`386` 为 32位 版。
:::

2. 解压后获得 `go-cqhttp.exe` 或 `./go-cqhttp`。运行 `go-cqhttp` 程序，会在同一目录下生成一个 `config.hjson` 文件。打开 `config.hjson` 修改如下内容（高亮行为需要改动的部分）

::: warning 注意
使用 Windows 自带记事本修改可能会导致编码问题，因此**强烈建议**使用第三方文本编辑器，如 [NotePad3](https://www.rizonesoft.com/downloads/notepad3/)，[VS Code](https://code.visualstudio.com/Download)，[Sublime Text](http://www.sublimetext.com/3)
:::

```hjson {7,9,49,56,74,85,89,91,93,99,110}
/*
    go-cqhttp 默认配置文件
*/

{
    // QQ号
    uin: 0
    // QQ密码
    password: ""
    // 是否启用密码加密
    encrypt_password: false
    // 加密后的密码, 如未启用密码加密将为空, 请勿随意修改.
    password_encrypted: ""
    // 是否启用内置数据库
    // 启用将会增加10-20MB的内存占用和一定的磁盘空间
    // 关闭将无法使用 撤回 回复 get_msg 等上下文相关功能
    enable_db: true
    // 访问密钥, 强烈推荐在公网的服务器设置
    access_token: ""
    // 重连设置
    relogin: {
        // 是否启用自动重连
        // 如不启用掉线后将不会自动重连
        enabled: true
        // 重连延迟, 单位秒
        relogin_delay: 3
        // 最大重连次数, 0为无限制
        max_relogin_times: 0
    }
    // API限速设置
    // 该设置为全局生效
    // 原 cqhttp 虽然启用了 rate_limit 后缀, 但是基本没插件适配
    // 目前该限速设置为令牌桶算法, 请参考: 
    // https://baike.baidu.com/item/%E4%BB%A4%E7%89%8C%E6%A1%B6%E7%AE%97%E6%B3%95/6597000?fr=aladdin
    _rate_limit: {
        // 是否启用限速
        enabled: false
        // 令牌回复频率, 单位秒
        frequency: 1
        // 令牌桶大小
        bucket_size: 1
    }
    // 是否忽略无效的CQ码
    // 如果为假将原样发送
    ignore_invalid_cqcode: false
    // 是否强制分片发送消息
    // 分片发送将会带来更快的速度
    // 但是兼容性会有些问题
    force_fragmented: true
    // 心跳频率, 单位秒
    // -1 为关闭心跳
    heartbeat_interval: 0
    // HTTP设置
    http_config: {
        // 是否启用正向HTTP服务器
        enabled: false
        // 服务端监听地址
        host: 0.0.0.0
        // 服务端监听端口
        port: 5700
        // 反向HTTP超时时间, 单位秒
        // 最小值为5，小于5将会忽略本项设置
        timeout: 0
        // 反向HTTP POST地址列表
        // 格式: 
        // {
        //    地址: secret
        // }
        post_urls: {}
    }
    // 正向WS设置
    ws_config: {
        // 是否启用正向WS服务器
        enabled: false
        // 正向WS服务器监听地址
        host: 0.0.0.0
        // 正向WS服务器监听端口
        port: 6700
    }
    // 反向WS设置
    ws_reverse_servers: [
        // 可以添加多个反向WS推送
        {
            // 是否启用该推送
            enabled: true
            // 反向WS Universal 地址
            // 注意 设置了此项地址后下面两项将会被忽略
            // 留空请使用 ""
            reverse_url: ws://127.0.0.1:8080/cqhttp/ws
            // 反向WS API 地址
            reverse_api_url: ""
            // 反向WS Event 地址
            reverse_event_url: ""
            reverse_reconnect_interval: 3000
        }
    ]
    // 上报数据类型
    // 可选: string array
    post_message_format: array
    // 是否使用服务器下发的新地址进行重连
    // 注意, 此设置可能导致在海外服务器上连接情况更差
    use_sso_address: false
    // 是否启用 DEBUG
    debug: false
    // 日志等级 trace,debug,info,warn,error
    log_level: "info"
    // WebUi 设置
    web_ui: {
        // 是否启用 WebUi
        enabled: false
        // 监听地址
        host: 127.0.0.1
        // 监听端口
        web_ui_port: 9999
        // 是否接收来自web的输入
        web_input: false
    }
}
```

3. 编辑完成后重新运行 `go-cqhttp`，跟随提示完成安全验证即可。滑块验证码相关请阅读 [go-cqhttp 文档](https://docs.go-cqhttp.org/faq/slider.html)。