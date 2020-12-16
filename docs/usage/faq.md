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