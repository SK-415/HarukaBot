#  安装 HarukaBot

::: warning 前提条件
HarukaBot 依赖于 [Python3.8+](https://www.python.org/downloads/release/python-386/)，不会安装的可以参考 [廖雪峰的教程](https://www.liaoxuefeng.com/wiki/1016959663602400/1016959856222624)。
:::

## 脚手架安装（推荐)

1. 打开终端，并选择一个文件夹用来存放数据。

    ::: tip Windows 用户可以这么做
    打开一个文件夹，对着文件夹内空白处，按住 shift 同时单击鼠标右键 -> 在此处打开 Powershell 窗口。
    :::

2. 安装脚手架。

    <code-group>
    <code-block title="pip">
    ```sh
    pip install hb-cli
    ```
    </code-block>

    <code-block title="poetry">
    ```sh
    poetry add hb-cli
    ```
    </code-block>
    </code-group>

3. 启动 HarukaBot。

    ```sh
    hb run
    ```

> 以后启动只需在**相同文件夹**内执行最后一步即可

## 从插件广场安装（适用于 `NoneBot2` 用户)

1. 使用 `nb-cli` 命令从[插件广场](https://v2.nonebot.dev/plugin-store.html)安装。

    ```sh
    nb plugin install haruka_bot
    ```

2. （可选）在 bot 根目录的 `.env.*` 文件中，添加 `HARUKA_DIR="./data/"` 设置 HarukaBot 数据文件的存储路径。你也可以将 `./data/` 改成任何其他路径。

    > 如果不添加，HarukaBot 会将数据文件保存于其安装包位置下（site-packages/haruka_bot/data），之后迁移会很麻烦，非常不推荐。

3. 在 `bot.py` 中，导入定时任务插件。

    ```python {1}
    nonebot.load_plugin('nonebot_plugin_apscheduler')
    nonebot.load_plugin('haruka_bot')
    ```

    ::: warning 注意
    `nonebot_plugin_apscheduler` 必须比 `haruka_bot` 先导入。
    :::

4. 安装完成后重启 `NoneBot2 实例` 即可使用。

## 从 GitHub 安装（包含尚未发布的特性）

已经按照上面两个方法之一安装完成后，可以从 GitHub 获取尚未发布的特性。

<code-group>
<code-block title="pip">
```sh
#master
pip install --upgrade git+https://github.com/SK-415/HarukaBot.git#master
#dev
pip install --upgrade git+https://github.com/SK-415/HarukaBot.git#dev
```
</code-block>

<code-block title="poetry">
```sh
#master
poetry add git+https://github.com/SK-415/HarukaBot.git#master
#dev
poetry add git+https://github.com/SK-415/HarukaBot.git#dev
```
</code-block>
</code-group>

##  手动安装（不推荐）

> 由于历史原因遗留的方法，不再提供支持，非常不推荐使用。

1. 克隆或下载 HarukaBot 源码到本地。

    ```sh
    git clone https://github.com/SK-415/HarukaBot.git
    ```

2. 安装依赖。

    <code-group>
    <code-block title="pip">
    ```sh
    pip install haruka-bot
    ```
    </code-block>

    <code-block title="poetry">
    ```sh
    poetry add haruka-bot
    ```
    </code-block>
    </code-group>

3. 启动 HarukaBot

    ```sh
    python bot.py
    ```

