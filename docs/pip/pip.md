# PIP（Python包管理工具）是什么
pip 是一个现代的，通用的python包管理工具。它提供了对Python包的查找、下载、安装、卸载等功能，是最常用的Python包管理工具之一。
pip自3.4Python 3和2.7.9Python 2 版本以来一直包含在Python安装程序中。

如果你足够细心，你将会在安装python是看到以下选项，我们以window 10 操作系统为例。

![python install](/pythoninstall.png)

## 我如何知道我是否有安装pip？
这一点也不困惑，如果你是上述版本之上的，你就有可能安装了pip。
你只需要打开PowerShell 输入：

> 提示：这里以windows 操作系统为例，如果你是其他操作系统，请尝试打开终端。打开powershell的方法请参照 [这里](https://jingyan.baidu.com/article/b907e62769217346e7891c8c.html)

```
pip -V
```
> **注意：** 这里的 **-V** 必须要大写。

你就能看到你的pip版本、位置，以及你的Python版本：
```
> pip 21.0.1 from c:\python\lib\site-packages\pip (python 3.9)
```
当然，如果没有正确返回，说明你的pip**没有安装**，或者**配置不正确**。

如果出现错误，别灰心，让我们开始安装pip。
## 我该如何安装pip呢？
如果你还未安装，则可以使用以下方法来安装：
在终端或者PowerShall中**连续执行**以下命令：

```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```
这会需要一点时间，如果不问题，你将会看到这样的信息：
```
....
Successfully installed pip-21.0.1
```
当然，安装失败也不要灰心，请检查**网络连接**与否安装python。

## 如何加快pip下载东西的速度？
pip安装软件前需要下载，下载东西的速度取决与你的带宽与服务器的链接质量，如果你位于国内，使用pip的国外源是非常不明智的选择，我们就要将它替换到国内源以求得更加流畅的使用体验。
如果你是使用windows操作系统，请你按照以下步骤操作：
**打开:** 此电脑> C盘 > 用户 > (你的用户名对应的文件夹)
新建一个文本文档，写入：
```
[global]
timeout = 6000
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.c
```
保存后退出，将文件重命名为 **pip.ini**,这是操作系统会提示，请选择**确认**。
> **注意：** **.ini**是扩展名，如果你不知道如何修改Windows操作系统下文件的扩展名，请查看[这里](https://www.baidu.com/s?wd=%E4%BF%AE%E6%94%B9%E6%96%87%E4%BB%B6%E6%89%A9%E5%B1%95%E5%90%8D)

完成上述操作步骤，你就完成了pip换源的所有操作。

## 如何使用pip呢？
pip的使用非常简单！你仅需在终端或者PowerShell中输入：
```
pip
```
你会惊奇的发现pip会告诉你如何正确的使用它。
我们来学习一些基础的pip命令。
### 安装
我们可以使用这个命令完成安装：
```
pip install 你要安装的包              # 最新版本
pip install 你要安装的包==1.0.4       # 指定版本
pip install '你要安装的包>=1.0.4'     # 最小版本
```
> 进阶：这样可以安装多个包：
pip install 你要安装的包1 你要安装的包2 ......

### 卸载
同样的，使用下列命令可以完成删除：
```
pip uninstall 你要卸载的包
```

## 探索更多...
上面仅介绍了一部分如何使用pip的方法，pip还有更多的功能，你可以在[这里](https://www.runoob.com/w3cnote/python-pip-install-usage.html)学到更多。


