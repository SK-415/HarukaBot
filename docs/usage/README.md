# 功能列表

::: warning 注意
群里使用命令前**需要** @机器人，如 `@HarukaBot 帮助`。

如果**不希望**在使用命令前 @机器人，请查看 [进阶配置](./settings)。
:::

## 帮助

获取目前 HarukaBot 支持的所有功能指令。

::: tip 提示
功能表会随版本变化，请以自己机器人帮助页面为准。
:::

<ClientOnly>
  ::: details 示例（点我展开）
  示例版本：v1.2.3
  <Messenger :messages="[
      { position: 'right', msg: '<a>@HarukaBot</a> 帮助' }, 
      { position: 'left', msg: 'DD机目前支持的功能有：\n\n主播列表\n开启权限\n关闭权限\n添加主播 uid\n删除主播 uid\n开启动态 uid\n关闭动态 uid\n开启直播 uid\n关闭直播 uid\n开启全体 uid\n关闭全体 uid\n版本信息\n\n命令中的uid需要替换为对应主播的uid，注意是uid不是直播间id\n\n群聊默认开启权限，只有管理员或机器人主人才能触发指令\n\n所有群聊/私聊的推送都是分开的，在哪里添加就只会在哪里推送' }
      ]"/>
  :::
</ClientOnly>

## 主播列表

获取**当前位置**（群聊/私聊）订阅的所有主播信息，以及相对应的各类推送信息的开关情况。

<ClientOnly>
  ::: details 示例（点我展开）
  示例版本：v1.2.3
  <Messenger :messages="[
      { position: 'right', msg: '<a>@HarukaBot</a> 主播列表' },
      { position: 'left', msg: '以下为当前的订阅列表：\n\n【白神遥Haruka】直播推送：开，动态推送：开（477332594）\n【SK_415】直播推送：开，动态推送：关（10352806）' }
      ]"/>
  :::
</ClientOnly>

## 开启权限 | 关闭权限

::: tip 提示

每个群一开始都**默认**为**开启权限**状态。

:::

::: warning 注意

即使关闭权限，普通群员也**无法使用** 开启权限、关闭权限、开启全体、关闭全体。

:::

`开启权限` 后，当前群内只有群主、管理员、和机器人主人（superuser）可以使用 HarukaBot。

`关闭权限` 后，所有人都可以使用 HaurkaBot。

<ClientOnly>
  ::: details 示例（点我展开）
  示例版本：v1.2.3
  <Messenger :messages="[
      { position: 'right', msg: '<a>@HarukaBot</a> 开启权限' },
      { position: 'left', msg: '已开启权限，只有管理员才能使用' },
      { position: 'right', msg: '<a>@HarukaBot</a> 关闭权限' },
      { position: 'left', msg: '已关闭权限，所有人都能使用' }
      ]"/>
  :::
</ClientOnly>

## 添加主播 | 删除主播

|参数|必须|
|--|--|
|[UID](./faq.md#如何查看别人的-uid)|:heavy_check_mark:|

::: warning 注意
每个群聊、私聊的推送列表都是相互独立的。你在任何位置的添加、删除以及其他修改操作都**不会影响**到其他位置的推送。
:::

在**当前位置**（群聊/私聊）添加或删除一位主播。

`添加主播` 后，在该主播开播、更新动态、发布视频时均会在**添加的位置**收到推送消息。

`删除主播` 后，将不会在**当前位置**（群聊/私聊）继续推送。

::: tip 提示
添加后的主播，**默认**会开启直播推送和动态推送，可以通过下面的命令来修改推送设置。
:::

<ClientOnly>
  ::: details 示例（点我展开）
  示例版本：v1.2.3
  <Messenger :messages="[
      { position: 'right', msg: '<a>@HarukaBot</a> 添加主播 477332594' },
      { position: 'left', msg: '已添加 白神遥Haruka（477332594）' },
      { position: 'right', msg: '<a>@HarukaBot</a> 删除主播 10352806' },
      { position: 'left', msg: '已删除 SK_415（10352806）' }
      ]"/>
  :::
</ClientOnly>

## 开启动态 | 关闭动态

|参数|必须|
|--|--|
|[UID](./faq.md#如何查看别人的-uid)|:heavy_check_mark:|

::: tip 提示
新添加的主播**默认开启**动态推送。
:::

`开启动态` 后，会在**当前位置**（群聊/私聊）推送主播新发的动态。

`关闭动态` 后，将不会在**当前位置**（群聊/私聊）继续推送。

<ClientOnly>
  ::: details 示例（点我展开）
  示例版本：v1.2.3
  <Messenger :messages="[
      { position: 'right', msg: '<a>@HarukaBot</a> 开启动态 477332594' },
      { position: 'left', msg: '已开启动态，白神遥Haruka（477332594）' },
      { position: 'right', msg: '<a>@HarukaBot</a> 关闭动态 10352806' },
      { position: 'left', msg: '已关闭动态，SK_415（10352806）' },
      { position: 'left', msg: '白神遥Haruka转发了一条动态：\n\n传送门→<a href=&quot;https://t.bilibili.com/455707574981546955&quot; target=&quot;_blank&quot;>https://t.bilibili.com/455707574981546955</a>\n<img src=&quot;/dynamic-example.png&quot;/>' }
      ]"/>
  :::
</ClientOnly>

## 开启直播 | 关闭直播

|参数|必须|
|--|--|
|[UID](./faq.md#如何查看别人的-uid)|:heavy_check_mark:|

::: tip 提示
新添加的主播**默认开启**直播推送。
:::

`开启直播` 后，会在**当前位置**（群聊/私聊）推送主播的开播提醒。

`关闭直播` 后，将不会在**当前位置**（群聊/私聊）继续推送。

<ClientOnly>
  ::: details 示例（点我展开）
  示例版本：v1.2.3
  <Messenger :messages="[
      { position: 'right', msg: '<a>@HarukaBot</a> 开启直播 477332594' },
      { position: 'left', msg: '已开启直播，白神遥Haruka（477332594）' },
      { position: 'right', msg: '<a>@HarukaBot</a> 关闭直播 10352806' },
      { position: 'left', msg: '已关闭直播，SK_415（10352806）' },
      { position: 'left', msg: '白神遥Haruka 开播啦！\n\n海豹学歌！耶耶耶\n传送门→<a href=&quot;https://live.bilibili.com/21652717&quot; target=&quot;_blank&quot;>https://live.bilibili.com/21652717</a>\n<img src=&quot;/live-example.jpg&quot;/>' }
      ]"/>
  :::
</ClientOnly>

## 开启全体 | 关闭全体

|参数|必须|
|--|--|
|[UID](./faq.md#如何查看别人的-uid)|:heavy_check_mark:|

::: tip 提示
新添加的主播**默认**关闭全体。
:::

`开启全体` 后，机器人将会在该主播的开播提醒消息前 @全体成员。

`关闭推送` 后，则不会 @全体成员。

::: warning 注意
一个 QQ号 一天只能 @全体成员 十次。这个次数**所有群**共享，不是每个群一天十次。开通会员可以提高次数上限。
:::

<ClientOnly>
  ::: details 示例（点我展开）
  示例版本：v1.2.3
  <Messenger :messages="[
      { position: 'right', msg: '<a>@HarukaBot</a> 开启全体 477332594' },
      { position: 'left', msg: '已开启全体，白神遥Haruka（477332594）' },
      { position: 'right', msg: '<a>@HarukaBot</a> 关闭全体 10352806' },
      { position: 'left', msg: '已关闭全体，SK_415（10352806）' },
      { position: 'left', msg: '<a>@全体成员</a> 白神遥Haruka 开播啦！\n\n海豹学歌！耶耶耶\n传送门→<a href=&quot;https://live.bilibili.com/21652717&quot; target=&quot;_blank&quot;>https://live.bilibili.com/21652717</a>\n<img src=&quot;/live-example.jpg&quot;/>' }
      ]"/>
  :::
</ClientOnly>

## 版本信息

获取 HarukaBot 当前版本信息。

<ClientOnly>
  ::: details 示例（点我展开）
  示例版本：v1.2.3
  <Messenger :messages="[
      { position: 'right', msg: '<a>@HarukaBot</a> 版本信息' },
      { position: 'left', msg: '当前 HarukaBot 版本：1.2.3\n\n使用中遇到问题欢迎加群反馈，\n群号：629574472\n\n常见问题：https://haruka-bot.live/usage/faq.html' }
      ]"/>
  :::
</ClientOnly>
