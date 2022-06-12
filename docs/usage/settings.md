# 进阶配置

HarukaBot 存在一些**非必须的**进阶配置项，用户可以在 `.env.prod` 或 `.env.dev` 文件中添加这些配置来改变 HarukaBot 的**默认行为**。

::: tip 提示
添加配置项只需在 `.env.*` 文件最底下另起一行直接添加即可。
::: details 示例（点我展开）
```json {7-8}
HOST=0.0.0.0
PORT=8080
SUPERUSERS=[]
NICKNAME=[]
COMMAND_START=[""]
COMMAND_SEP=["."]
HARUKA_DIR="./data/"
HARUKA_TO_ME=false
```
:::

## HARUKA_DIR

默认值：None

修改数据文件默认存储路径，默认存在 `haruka-bot` 包安装目录下。

**不推荐**使用默认存储位置，这会使得数据文件迁移与管理异常麻烦。**推荐**设置 `HARUKA_DIR="./data/"`，即当前目录的 `data` 文件夹下。

::: tip 提示
如果使用 `hb-cli` 部署，会**自动**在 `.env.prod` 中添加 `HARUKA_DIR="./data/"`。
:::

```json
HARUKA_DIR="./data/"
```

## HARUKA_TO_ME

默认值：True

在群里使用命令前是否需要 @机器人。设置为 `False` 则可以直接触发指令。

```json
Haruka_TO_ME=False
```

## HARUKA_LIVE_OFF_NOTIFY

默认值：False

是否开启下播提醒。
```json
HARUKA_LIVE_OFF_NOTIFY=True
```

## HARUKA_PROXY

默认值：None

设置后所有网络请求将使用代理端口，仅支持 HTTP 代理。
```json
HARUKA_PROXY=http://127.0.0.1:10809
```

## HARUKA_INTERVAL

默认值：10

不推荐使用，请更换为 `HARUKA_LIVE_INTERVAL`。
直播刷新间隔，单位：秒。
```json
HARUKA_INTERVAL=20
```

## HARUKA_DYNAMIC_INTERVAL

默认值：1

动态刷新间隔，单位：秒。
```json
HARUKA_INTERVAL=5
```

## HARUKA_LIVE_INTERVAL

默认值：`HARUKA_INTERVAL` 的值

直播刷新间隔，单位：秒。
```json
HARUKA_INTERVAL=20
```

## HARUKA_DYNAMIC_AT

默认值：False

动态、投稿是否也要@全体。
```json
HARUKA_DYNAMIC_AT=True
```
