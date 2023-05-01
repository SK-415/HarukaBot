/*
 * @Author: KBD
 * @Date: 2022-12-26 13:45:30
 * @LastEditors: KBD
 * @LastEditTime: 2023-01-13 01:35:34
 * @Description: 用于初始化手机动态页面的样式以及图片大小
 */
async function getMobileStyle() {
    // 删除 dom 的对象, 可以自行添加 ( className 需要增加 '.' 为前缀, id 需要增加 '#' 为前缀)
    const deleteDoms = {
        // 关注 dom
        followDoms: [".dyn-header__following", ".easy-follow-btn"],
        // 分享 dom
        shareDoms: [".dyn-share"],
        // 打开程序 dom
        openAppBtnDoms: [".dynamic-float-btn", ".float-openapp"],
        // 导航 dom
        navDoms: [".m-navbar", ".opus-nav"],
        // 获取更多 dom
        readMoreDoms: [".opus-read-more"],
        // 全屏弹出 Dom
        openAppDialogDoms: [".openapp-dialog"],
        // 评论区 dom
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

    // // 新版动态需要给 bm-pics-block 的父级元素设置 flex 以及 column
    // const newContainerDom = document.querySelector(".bm-pics-block")?.parentElement;
    // if (newContainerDom) {
    //     // 设置为 flex
    //     newContainerDom.style.display = "flex";
    //     // 设置为竖向排列
    //     newContainerDom.style.flexDirection = "column";
    //     // flex - 垂直居中
    //     newContainerDom.style.justifyContent = "center";
    //     // flex - 水平居中
    //     newContainerDom.style.alignItems = "center";
    // }

    // 设置 mopus 的 paddingTop 为 0
    const mOpusDom = document.querySelector(".m-opus");
    if (mOpusDom) {
        mOpusDom.style.paddingTop = "0";
        mOpusDom.style.minHeight = "0";
    }

    // 删除老版动态 .dyn-card 上的字体设置
    const dynCardDom = document.querySelector(".dyn-card");
    if (dynCardDom) {
        dynCardDom.style.fontFamily = "unset";
    }

    // // 找到图标容器dom
    // const containerDom = document.querySelector(".bm-pics-block__container");
    // if (containerDom) {
    //     // 先把默认 padding-left 置为0
    //     containerDom.style.paddingLeft = "0";
    //     // 先把默认 padding-right 置为0
    //     containerDom.style.paddingRight = "0";
    //     // 设置 flex 模式下以列形式排列
    //     containerDom.style.flexDirection = "column";
    //     // 设置 flex 模式下每个容器间隔15px
    //     containerDom.style.gap = "15px";
    //     // flex - 垂直居中
    //     containerDom.style.justifyContent = "center";
    //     // flex - 水平居中
    //     containerDom.style.alignItems = "center";
    // }

    // 获取图片容器的所有 dom
    const imageItemDoms = document.querySelectorAll(".bm-pics-block__item");

    // 异步遍历图片 dom
    Array.from(imageItemDoms).map(async (item) => {
        // // 获取屏幕比例的 90% 宽度
        // const clientWidth = window.innerWidth * 0.9;
        // // 先把默认 margin 置为 0
        // item.style.margin = "0";
        // // 宽度默认撑满屏幕宽度 90%;
        // item.style.width = `${clientWidth}px`;
        // 获取原app中图片的src
        const imgSrc = item.firstChild.src;
        // 判断是否有 @ 符
        const imgSrcAtIndex = imgSrc.indexOf("@");
        // 将所有图片转换为 .webp 格式节省加载速度, 并返回给原来的 image 标签
        item.firstChild.src = imgSrcAtIndex !== -1 ? imgSrc.slice(0, imgSrcAtIndex + 1) + ".webp" : imgSrc;
        // // 设置自动高度
        // item.style.height = "auto";
    })
}


function setFont(font = "", fontSource = "local") {
    // TODO: 未来考虑添加本地离线字体
    // 自行添加在线字体(字体的优先度将按照顺序执行)
    const needLoadFontList = [
        {
            fontUrl: "https://cdn.jsdelivr.net/gh/irozhi/HarmonyOS-Sans/HarmonyOS_Sans_SC/HarmonyOS_Sans_SC_Medium.woff2",
            fontFamily: "HarmonyOS_Medium_woff2",
        }
    ];
    const emojiFontList = ["Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"];

    if (font) {
        // 如果传入了字体名, 则将其添加到字体列表首位
        if (fontSource === "local") {
            needLoadFontList.unshift({
                fontUrl: `https://fonts.bbot/${font}`,
                fontFamily: "BBot_Custom_Font",
            });
        } else if (fontSource === "remote") {
            needLoadFontList.unshift({
                fontUrl: font,
                fontFamily: "BBot_Custom_Font",
            });
        }
    }

    // 字体按需加载方法
    (() => {
        const code = needLoadFontList.reduce((defaultString, fontObject) => {
            return defaultString + `@font-face { font-family: ${fontObject.fontFamily};src: url('${fontObject.fontUrl}'); }`;
        }, "");
        const style = document.createElement("style");
        style.rel = "stylesheet";
        style.appendChild(document.createTextNode(code));
        const head = document.getElementsByTagName("head")[0];
        head.appendChild(style);
    })();

    // 将字体样式设置到 div#app 上
    const appDom = document.querySelector("#app");
    const emojiFont = emojiFontList.join(",");
    if (appDom) {
        // 动态加字体, 并给与默认值 sans-serif
        if (fontSource === "system") {
            appDom.style.fontFamily = font + "," + emojiFont + ",sans-serif";
        } else {
            const needLoadFont = needLoadFontList.reduce((defaultString, fontObject) => defaultString + fontObject.fontFamily + ",", "");
            appDom.style.fontFamily = needLoadFont + emojiFont + ",sans-serif";
        };
        appDom.style.overflowWrap = "break-word";
    }

    return font;
}


async function imageComplete() {
    // 异步渲染已经加载的图片地址, 如果已经缓存则会立即返回 true
    const loadImageAsync = (url) => {
        return new Promise((resolve, reject) => {
            const image = new Image();
            image.src = url;

            image.onload = () => {
                resolve(image.complete) // 理应为 true
            }

            image.onerror = () => {
                reject(false);
            }
        })
    }

    // 获取图片容器的所有 dom
    const imageItemDoms = document.querySelectorAll(".bm-pics-block__item");

    // 异步遍历图片并等待
    const imageItemStatusArray = await Promise.all(Array.from(imageItemDoms).map((item) => {
        return loadImageAsync(item.firstChild.src);
    }))

    // 通过遍历图片加载状态, 如果有一个图片加载失败, 均为 false
    return imageItemStatusArray.reduce((p, c) => {
        return p && c;
    }, true)
}

function fontsLoaded() {
    // 判断字体是否都加载完成
    return document.fonts.status === "loaded";
}

window.onload = () => {
    getMobileStyle();
}