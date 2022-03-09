#  安装 HarukaBot

::: warning 前提条件
HarukaBot 基于 [NoneBot2](https://github.com/nonebot/nonebot2) 开发，因此依赖于 [Python3.8+](https://www.python.org/downloads/release/python-386/)。不会安装 Python 的可以参考 [廖雪峰的教程](https://www.liaoxuefeng.com/wiki/1016959663602400/1016959856222624)。
:::

::: danger 警告

[NoneBot2](https://github.com/nonebot/nonebot2) 与 [NoneBot](https://github.com/nonebot/nonebot) **不兼容且无法共存**！如果你曾经使用过 NoneBot 或基于 NoneBot 开发的机器人（如：[yobot](https://github.com/pcrbot/yobot)、[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)、[dd-bot](https://github.com/SK-415/dd-bot)），或者你不确定是否安装过 NoneBot。

那么在**开始安装之前**，请先尝试在终端（Powershell/cmd）内执行 `pip uninstall nonebot` **卸载** NoneBot，或者创建一个 [虚拟环境](https://docs.python.org/zh-cn/3/library/venv.html#creating-virtual-environments) 使 HarukaBot 可以与 NoneBot 共存。
 :::

## 脚手架安装（推荐）

1. 打开终端，并选择一个文件夹用来存放数据。

    ::: tip Windows 用户可以这么做
    打开一个文件夹，对着文件夹内空白处，按住 shift 同时单击鼠标右键 -> 在此处打开 Powershell/命令 窗口。
    :::

2. 在终端内输入以下命令安装脚手架。

    :::: code-group
    ::: code-group-item pip

    ```sh
    pip install haruka-bot
    ```
    :::

    ::: code-group-item poetry

    ```sh
    poetry add haruka-bot
    ```
    :::
    ::::

    ::: tip 下载慢可以尝试清华源
    <CodeGroup>
    <CodeGroupItem title="pip">

    ```sh
    pip install haruka-bot -i https://pypi.tuna.tsinghua.edu.cn/simple/
    ```
    </CodeGroupItem>
    <CodeGroupItem title="poetry">

    ```sh
    请参考：https://python-poetry.org/docs/repositories/#install-dependencies-from-a-private-repository
    ```
    </CodeGroupItem>
    </CodeGroup>
    :::

3. 启动 HarukaBot。

    ```sh
    hb run
    ```

> 以后启动只需在**相同文件夹**内执行最后一步即可

::: tip 怎么更新 HarukaBot？
详见 [常见问题](/faq.md#怎么更新-harukabot)
:::

## 从 NoneBot2 插件商店安装（适用于 NoneBot2 用户）

1. 使用 `nb-cli` 命令从 [NoneBot2 商店](https://v2.nonebot.dev/store.html) 安装。

    ```sh
    nb plugin install haruka_bot
    ```

2. （可选）在 bot 根目录的 `.env.*` 文件中，添加 `HARUKA_DIR="储存路径"` （不设置默认为 `./data/`）设置 HarukaBot 数据文件的存储路径。

3. 安装完成后重启 `NoneBot2 项目` 即可使用。

## 从 GitHub 安装（包含不稳定的新特性）

安装

:::: code-group
::: code-group-item pip

```sh
#master
pip install --upgrade git+https://github.com/SK-415/HarukaBot.git#master
#dev
pip install --upgrade git+https://github.com/SK-415/HarukaBot.git#dev
```
:::

::: code-group-item poetry

```sh
#master
poetry add git+https://github.com/SK-415/HarukaBot.git#master
#dev
poetry add git+https://github.com/SK-415/HarukaBot.git#dev
```
:::
::::

运行

```sh
hb run
```

##  手动安装（不推荐）

> 由于历史原因遗留的方法，不再提供支持，非常不推荐使用。

1. 克隆或下载 HarukaBot 源码到本地。

    ```sh
    git clone https://github.com/SK-415/HarukaBot.git
    ```

2. 安装依赖。

    ```sh
    poetry install --no-dev
    ```

3. 启动 HarukaBot

    ```sh
    python bot.py
    ```

