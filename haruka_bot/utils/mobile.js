/*
 * @Author: KBD
 * @Date: 2022-12-26 13:45:30
 * @LastEditors: KBD
 * @LastEditTime: 2023-01-11 15:18:13
 * @Description: 用于初始化手机动态页面的样式以及图片大小
 */
async function getMobileStyle() {
    // 删除dom的Object, 可以自行添加 (className需要增加'.'为前缀, id需要增加'#'为前缀)
    const deleteDoms = {
        // 关注dom
        followDoms: [".dyn-header__following", ".easy-follow-btn"],
        // 分享dom
        shareDoms: [".dyn-share"],
        // 打开程序dom
        openAppBtnDoms: [".dynamic-float-btn", ".float-openapp"],
        // 导航dom
        navDoms: [".m-navbar", ".opus-nav"],
        // 获取更多dom
        readMoreDoms: [".opus-read-more"],
        // 全屏弹出Dom
        openAppDialogDoms: [".openapp-dialog"],
        // 评论区dom
        commentsDoms: [".v-switcher"],
    }

    // 遍历对象的值, 并将多数组扁平化, 再遍历进行删除操作
    Object.values(deleteDoms).flat(1).forEach(domTag => {
        const deleteDom = document.querySelector(domTag);
        deleteDom && deleteDom.remove();
    })

    // 新版动态需要移除对应 class 达到跳过点击事件, 解除隐藏的目的 
    const contentDom = document.querySelector(".opus-module-content");
    contentDom && contentDom.classList.remove("limit");

    // 新版动态需要给 bm-pics-block 的父级元素设置 flex 以及 column
    const newContainerDom = document.querySelector(".bm-pics-block")?.parentElement;
    if (newContainerDom) {
        // 设置为 flex
        newContainerDom.style.display = "flex";
        // 设置为竖向排列
        newContainerDom.style.flexDirection = "column";
        // flex - 垂直居中
        newContainerDom.style.justifyContent = "center";
        // flex - 水平居中
        newContainerDom.style.alignItems = "center";
    }

    // 设置 mopus 的 paddingTop 为 0
    const mOpusDom = document.querySelector(".m-opus");
    if (mOpusDom) {
        mOpusDom.style.paddingTop = "0";
        mOpusDom.style.minHeight = "0";
    }

    // 设置字体格式
    const cardDom = document.querySelector(".dyn-card");
    if (cardDom) {
        cardDom.style.fontFamily = "Noto Sans CJK SC, sans-serif";
        cardDom.style.overflowWrap = "break-word";
    }

    // 找到图标容器dom
    const containerDom = document.querySelector(".bm-pics-block__container");
    if (containerDom) {
        // 先把默认padding-left置为0
        containerDom.style.paddingLeft = "0";
        // 先把默认padding-right置为0
        containerDom.style.paddingRight = "0";
        // 设置flex模式下以列形式排列
        containerDom.style.flexDirection = "column";
        // 设置flex模式下每个容器间隔15px
        containerDom.style.gap = "15px";
        // flex - 垂直居中
        containerDom.style.justifyContent = "center";
        // flex - 水平居中
        containerDom.style.alignItems = "center";
    }

    // 定义异步方法获取图片原尺寸(仅限于dom上的src路径的图片原尺寸)
    const getImageSize = (url) => {
        return new Promise((resolve, reject) => {
            const image = new Image();
            image.onload = () => {
                // 图片加载成功返回对象(包含长宽)
                resolve({
                    width: image.width, height: image.height,
                });
            };
            image.onerror = () => {
                reject(new Error("error"));
            };
            image.src = url;
        });
    };

    // 获取图片容器的所有dom
    const imageItemDoms = document.querySelectorAll(".bm-pics-block__item");

    // 异步遍历图片dom
    await Promise.all(Array.from(imageItemDoms).map(async (item) => {
        // 获取屏幕比例的90%宽度
        const clientWidth = window.innerWidth * 0.9;

        // 先把默认margin置为0
        item.style.margin = "0";
        // 宽度默认撑满屏幕宽度90%;
        item.style.width = `${clientWidth}px`;
        try {
            // 初始化url
            let imageTrueUrl;

            // 获取原app中图片的src
            const imgSrc = item.firstChild.src;
            // 判断是否有@符
            const imgSrcAtIndex = imgSrc.indexOf("@");

            // 将所有图片转换为.webp格式节省加载速度
            imageTrueUrl = imgSrcAtIndex !== -1 ? imgSrc.slice(0, imgSrcAtIndex + 1) + ".webp" : imgSrc;

            // 需要将真实的路径返回给image标签上(否则会失真)
            item.firstChild.src = imageTrueUrl;

            // 获取图片原尺寸对象
            const obj = await getImageSize(imageTrueUrl);
            // 图片大小判断逻辑部分(以屏幕宽度90%的1:1为基准)
            if (obj.width / obj.height !== 1) {
                item.style.height = `${(clientWidth / obj.width) * obj.height}px`;
            } else {
                item.style.height = "auto";
            }
        } catch (err) {
            item.style.height = "auto";
        }
    }))
}

window.onload = () => {
    getMobileStyle();
}