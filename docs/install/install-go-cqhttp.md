# 安装 go-cqhttp

::: warning 注意
HarukaBot 一直是使用 go-cqhttp 进行开发的，同时适配了个别 go-cqhttp 独有的实现（如：`set_restart api`）。

因此，**非常不建议**使用其他的 cqhttp 实现来代替 go-cqhttp，除非你愿意承担兼容性问题引发的后果。
:::

下载 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp/releases/latest)（Windows 用户选择 `windows-amd64.zip` 结尾）。

解压后或得 `go-cqhttp.exe`，在同目录下创建一个 `config.json` 文件，打开并填入如下内容：

::: details 不会替换 QQ号 与 QQ密码？（点我展开）
修改 2-3 行为自己机器人的 QQ号 和 QQ密码，例如：
```json
"uin": 12345,
"password": "abcd1234",
```
:::

```json {2-3}
{
	"uin": QQ号,
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
	},
	"ws_config": {
		"enabled": false,
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
	"web_ui": {
		"enabled": false,
	}
}
```
  
编辑完重启 `go-cqhttp.exe`，跟随提示完成安全验证即可。