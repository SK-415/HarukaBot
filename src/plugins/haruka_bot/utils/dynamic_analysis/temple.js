



//将时间戳转换为标准时间格式
function time(time = +new Date()) {
    var date = new Date(time + 8 * 3600 * 1000); // 增加8小时
    return date.toJSON().substr(0, 19).replace('T', ' ');
}


//设置主体大致信息
function user_info_process(info) {
    //认证状态
    var official_verify = info.desc.user_profile.card.official_verify.type;

    //时间戳
    var timestamp = info.desc.timestamp;

    //设置头像
    $(".face").css({ "background-image": "url('" + info.desc.user_profile.info.face + "@96w_96h_1c.webp" + "')", });

    //找找是否有头像挂件有的话设置个挂件
    if (info.desc.user_profile.pendant.image_enhance !== "") {
        $(".avatar").before("<div class='pendent'></div>")
        var image_enhance = info.desc.user_profile.pendant.image_enhance + "@163w_163h.webp";
        $(".pendant").css({ "background-image": "url('" + image_enhance + "')", })
    }

    // 找到昵称所在的div
    var name_tag = $(".user-name");

    //设置昵称的文字
    name_tag.text(info.desc.user_profile.info.uname);

    //设置昵称的颜色

    name_tag.css("color", info.desc.user_profile.vip.nickname_color);

    //time(timestamp * 1000)为将时间戳转换为时间格式
    var time_formate = time(timestamp * 1000)

    //设置时间
    $(".time").text(time_formate);


    //设置二维码
    $(".qrcode").qrcode({
        render: "canvas",
        correctLevel: 1,
        text: "https://t.bilibili.com/" + info.desc.dynamic_id_str,
        width: 60,
        height: 60,
    });


    // 根据不同的认证类型设置不同颜色的小闪电
    var official_verify_tag = $(".verify");
    switch (official_verify) {
        //0为黄色小闪电
        case 0:
            official_verify_tag.css({ "background-image": "url('" + "pic/official_yellow.png" + "')" });
            break;
        //1是蓝色小闪电
        case 1:
            official_verify_tag.css({ "background-image": "url('" + "pic/official_blue.png" + "')" });
            break;
        //-1是未认证,将认证图标所在的div隐藏起来
        case -1:
            official_verify_tag.css("display", "none");
            break;
    }
}

//找到动态文字主体
function find_desc(type, card) {
    //专栏是没有文字部分的
    var description
    switch (type) {
        //转发的动态
        case 1:
            description = card.item.content;
            return description;
        //发送了一条带图片的动态
        case 2:
            description = card.item.description;
            return description;
        //发送了一条纯文字动态
        case 4:
            description = card.item.content;
            return description;
        //发送了新投稿视频
        case 8:
            description = card.dynamic;
            return description
        // //音频
        case 256:
            description = card.intro;
            return description
        //使用了装扮
        case 2048:
        case 2049:
            description = card.vest.content;
            return description


    }
}

// 找到at
function find_ctrl(type, inner_card) {
    var ctrl
    var extend_json
    switch (type) {
        //转发了一条动态
        case 1:
            if (inner_card.item.hasOwnProperty("ctrl")) {
                ctrl = inner_card.item.ctrl;
                if (ctrl.length !== 0) {
                    ctrl = JSON.parse(ctrl);
                    return ctrl
                } else {
                    return
                }
            } else {
                return
            }
        //发送了一条带图片的动态
        case 2:
            ctrl = inner_card.item.at_control;
            if (ctrl.length !== 0) {
                ctrl = JSON.parse(ctrl);
                return ctrl
            } else {
                return
            }
        //发送了一条纯文字动态
        case 4:
            ctrl = inner_card.item.ctrl;
            if (ctrl !== undefined && ctrl.length !== 0) {
                ctrl = JSON.parse(ctrl);
                return ctrl
            } else {
                return
            }
        //发送了新投稿视频
        case 8:
            if (card.desc.type === 8) {
                extend_json = JSON.parse(card.extend_json);
                if (extend_json.hasOwnProperty("ctrl")) {
                    ctrl = extend_json.ctrl;
                    if (ctrl.length !== 0) {
                        return ctrl
                    } else {
                        return
                    }
                } else {
                    return
                }
            } else {
                extend_json = JSON.parse(JSON.parse(card.card).origin_extend_json);
                if (extend_json.hasOwnProperty("ctrl")) {
                    ctrl = extend_json.ctrl;
                    if (ctrl.length !== 0) {
                        return ctrl
                    } else {
                        return
                    }
                } else {
                    return
                }
            }
        case 2048:
            if (card.desc.type === 2048) {
                extend_json = JSON.parse(card.extend_json);
                if (extend_json.hasOwnProperty("at_control")) {
                    ctrl = extend_json.at_control;
                    if (ctrl.length !== 0) {
                        return ctrl
                    } else {
                        return
                    }
                } else {
                    return
                }
            } else {
                extend_json = JSON.parse(JSON.parse(card.card)["origin_extend_json"]);
                if (extend_json.hasOwnProperty("at_control")) {
                    ctrl = extend_json.at_control;
                    if (ctrl.length !== 0) {
                        return ctrl
                    } else {
                        return
                    }
                } else {
                    return
                }
            }
    }

}

//找到话题所在的对象
function find_topic(info, type) {
    //有的时候没有display
    if (info.hasOwnProperty("display")) {
        var display = info.display;
        //0和1区分转发动态和普通动态
        switch (type) {
            case 0:
                //原文中没有话题的时候,display中就没有topic_info这个key
                if (display.hasOwnProperty("topic_info")) {
                    return display.topic_info.topic_details
                } else {
                    return
                }
            case 1:
                //被转发的原文中没有话题和emoji的时候,display中就没有origin这个key
                if (display.hasOwnProperty("origin")) {
                    var origin = display.origin
                    //有origin但是没有话题只有emoji的时候就没有topic_info这个key
                    if (origin.hasOwnProperty("topic_info")) {
                        return origin.topic_info.topic_details
                    }
                }
        }
    }
}

// 找到emoji
function find_emoji(info, type) {
    //类比上边的find_topic
    if (info.hasOwnProperty("display")) {
        var display = info.display
        switch (type) {
            case 0:
                if (display.hasOwnProperty("emoji_info")) {
                    return display.emoji_info.emoji_details;
                } else {
                    return
                }
            case 1:
                if (display.hasOwnProperty("origin")) {
                    var origin = display.origin
                    if (origin.hasOwnProperty("emoji_info")) {
                        return origin.emoji_info.emoji_details;
                    }
                }
        }
    }
}

// 找到富文本
function find_rich_text(info, type) {
    if (info.hasOwnProperty("display")) {
        var display = info.display;
        switch (type) {
            case 0:
                //原文中没有话题的时候,display中就没有topic_info这个key
                if (display.hasOwnProperty("rich_text")) {
                    return display.rich_text.rich_details
                } else {
                    return
                }
            case 1:
                //被转发的原文中没有话题和emoji的时候,display中就没有origin这个key
                if (display.hasOwnProperty("origin")) {
                    var origin = display.origin
                    //有origin但是没有话题只有emoji的时候就没有topic_info这个key
                    if (origin.hasOwnProperty("rich_text")) {
                        return origin.rich_text.rich_details
                    }
                }
        }


    }


}

// 对文本中的at进行处理
function at_process(description, ctrl) {
    var ctrl_tag_list = [];
    for (i = 0; i < ctrl.length; i++) {
        //ctrl的起始位置
        var location = ctrl[i]['location'];
        //ctrl的类型,因为ctrl类型为2的时候为抽奖,3的时候为投票,所以要区分一下
        var c_typy = ctrl[i]["type"];
        //ctrl最后一个字符的位置
        var end;
        //用一个对象来装ctrl的具体内容以及其type以便于后续将原文中的ctrl的内容换成标签
        var tag_dic = new Array();
        switch (c_typy) {
            // at
            case 1:
                end = location + parseInt(ctrl[i]["length"]);
                tag_dic["content"] = description.slice(location, end);
                tag_dic["type"] = c_typy;
                ctrl_tag_list.push(tag_dic);
                break;
            //抽奖
            case 2:
            case 3:
            case 4:
                end = location + parseInt(ctrl[i]["data"]);
                tag_dic["content"] = description.slice(location, end);
                tag_dic["type"] = c_typy;
                ctrl_tag_list.push(tag_dic);
                break
        }
    }
    for (i = 0; i < ctrl_tag_list.length; i++) {
        var img_tag
        var text_tag
        switch (ctrl_tag_list[i]["type"]) {
            //at
            case 1:
                var reg = new RegExp(ctrl_tag_list[i]["content"], "g");
                description = description.replace(reg, "<a style='color:#178bcf;'>" + ctrl_tag_list[i]["content"] + "</a>");
                break;
            //抽奖
            case 2:
                img_tag = "<img class='lottery' src='" + "pic/lottery.png" + "'>";
                text_tag = "<a style='color:#178bcf;'>" + ctrl_tag_list[i]["content"] + "</a>";
                description = description.replace(ctrl_tag_list[i]["content"], img_tag + text_tag);
                break;
            //投票
            case 3:
                img_tag = "<img class='vote' src='" + "pic/vote.png" + "'>";
                text_tag = "<a style='color:#178bcf;'>" + ctrl_tag_list[i]["content"] + "</a>";
                description = description.replace(ctrl_tag_list[i]["content"], img_tag + text_tag);
                break;
            //淘宝
            case 4:
                img_tag = "<img class='taobao' src='" + "pic/taobao.png" + "'>";
                text_tag = "<a style='color:#178bcf;'>" + ctrl_tag_list[i]["content"] + "</a>";
                var re = new RegExp(ctrl_tag_list[i]["content"] + "(?!<)", "g")
                description = description.replace(re, img_tag + text_tag);
                break;
        }
    }
    return description

}

//对话题进行处理
function topic_process(desciption, topic_list) {
    for (i = 0; i < topic_list.length; i++) {
        //topic_name只有文字,所以手动给它加两个＃
        var topic_name = "#" + topic_list[i]["topic_name"] + "#";
        // 将原文中的topic换成a标签
        var re = new RegExp(topic_name + "(?!<a class=topic)", "g")
        desciption = desciption.replace(re, "<a class=topic style='color:#178bcf;'>" + topic_name + "</a>");
    }
    return desciption
}

//对表情进行处理
function emoji_process(desciption, emoji_list) {
    //遍历emoji_list
    for (i = 0; i < emoji_list.length; i++) {
        var emoji_name = emoji_list[i]["emoji_name"];
        var emoji_url = emoji_list[i]["url"];
        var emoji_tag = "<img class='emoji'  src='" + emoji_url + "'/>";
        //显然这是通过emoji_list中的emoji_name,将原文中的emoji_name换成img标签
        while (desciption.indexOf(emoji_name) !== -1) {
            desciption = desciption.replace(emoji_name, emoji_tag);
        }
    }
    return desciption
}

//对富文本进行处理
function richtext_process(desciption, richtext_list) {
    for (i = 0; i < richtext_list.length; i++) {
        var orig_text = richtext_list[i]["orig_text"];
        var text = richtext_list[i]["text"];
        var text_tag
        var reg
        switch (richtext_list[i]["icon_type"]) {
            case 1:
                reg = new RegExp(orig_text, "g");
                text_tag = "<a class = 'dynamic-link-hover-bg' style='color:#178bcf'><img class='rich-text-img' src='pic/play.png'>" + text + "</a>";
                desciption = desciption.replace(reg, text_tag);
                break;
            case 2:
                reg = new RegExp(orig_text, "g");
                text_tag = "<a class = 'dynamic-link-hover-bg' style='color:#178bcf'><img class='rich-text-img' src='pic/article.png'>" + text + "</a>";
                desciption = desciption.replace(reg, text_tag);

        }
    }
    return desciption


}

// 对文本中的B站链接进行处理
function httpString(description) {
    var reg = /(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?/g;
    var url_list = description.match(reg);
    if (url_list !== null) {
        var matcht = /^(https?:\/\/)([0-9a-z.]+)(:[0-9]+)?([/0-9a-z.]+)?(\?[0-9a-z&=]+)?(#[0-9-a-z]+)?/i;
        url_list.forEach((url) => {
            var result = matcht.exec(url);
            var domin_list = ["t.bilibili.com", "live.bilibili.com", "www.bilibili.com", "space.bilibili.com","m.bilibili.com","mall.bilibili.com","b23.tv"];
            if (domin_list.indexOf(result[2]) !== -1) {
                var link_tag = "<img class='web-link' src='" + "pic/link.png" + "'>";
                var text_tag = "<a style='color:#178bcf;'>" + "网页链接" + "</a>";
                var re = new RegExp(url, "g");
                while (description.indexOf(url) !== -1) {
                    description = description.replace(url, link_tag + text_tag);
                }
            }
        })
        return description;
    } else {
        return description;
    }
}

// 对add_on_card进行处理

function add_on_card_info(cards, type) {
    var title;
    var desc_first;
    var desc_second;
    var cover_url
    var add_on_card_show_type;
    //转发的动态的type是1，本人发的动态的type是0
    switch (type) {
        case 0:
            if (cards.hasOwnProperty("display")) {
                if (cards["display"].hasOwnProperty("add_on_card_info")) {
                    //add_on_card_show_type：6是直播预约，3是投票，2是游戏或者装扮推荐,5是追加视频
                    add_on_card_show_type = cards.display.add_on_card_info[0].add_on_card_show_type;
                    switch (add_on_card_show_type) {
                        case 6:
                            $(".reserve").css({ "display": "block" });
                            title = cards.display.add_on_card_info[0].reserve_attach_card.title;
                            desc_first = cards.display.add_on_card_info[0].reserve_attach_card.desc_first.text;
                            desc_second = cards.display.add_on_card_info[0].reserve_attach_card.desc_second;
                            $(".reserve-desc-first").text(desc_first);
                            $(".reserve-desc-second").text(desc_second);
                            $(".reserve-title").text(title);
                            break;
                        case 2:
                            $(".game").css({ "display": "block" });
                            title = cards.display.add_on_card_info[0].attach_card.title;
                            desc_first = cards.display.add_on_card_info[0].attach_card.desc_first;
                            desc_second = cards.display.add_on_card_info[0].attach_card.desc_second;
                            cover_url = cards.display.add_on_card_info[0].attach_card.cover_url;
                            $(".game-cover").css({ "background-image": "url('" + cover_url + "')" });
                            console.log(title);
                            $(".game-title").text(title);
                            $(".game-desc-fist").text(desc_first)
                            $(".game-desc-second").text(desc_second)
                            break;
                        case 3:
                            break;
                        case 5:
                            //605411280011530522
                            break;

                    }
                }
            }
            break;
        case 1:
            if (cards.hasOwnProperty("display")) {
                if (cards.display.hasOwnProperty("origin") && cards.display.origin.add_on_card_info) {
                    //add_on_card_show_type：6是直播预约，3是投票，2是游戏
                    add_on_card_show_type = cards.display.origin.add_on_card_info[0].add_on_card_show_type;
                    switch (add_on_card_show_type) {
                        case 6:
                            $(".repost-reserve").css({ "display": "block" });
                            title = cards.display.origin.add_on_card_info[0].reserve_attach_card.title;
                            desc_first = cards.display.origin.add_on_card_info[0].reserve_attach_card.desc_first.text;
                            desc_second = cards.display.origin.add_on_card_info[0].reserve_attach_card.desc_second;
                            $(".repost-reserve-desc-first").text(desc_first);
                            $(".repost-reserve-desc-second").text(desc_second);
                            $(".repost-reserve-title").text(title);
                            break;
                        case 2:
                            $(".repost-game").css("display", "block")
                            cover_url = cards.display.origin.add_on_card_info[0].attach_card.cover_url;
                            title = cards.display.origin.add_on_card_info[0].attach_card.title;
                            desc_first = cards.display.origin.add_on_card_info[0].attach_card.desc_first;
                            desc_second = cards.display.origin.add_on_card_info[0].attach_card.desc_second;
                            $(".repost-game-cover").css({ "background-image": "url('" + cover_url + "')" });
                            $(".repost-game-title").text(title);
                            $(".repost-game-desc-fist").text(desc_first);
                            $(".repost-game-desc-second").text(desc_second);
                            break;
                        //一般投票类型的add_on_card在网页端都不会显示，所以不用做处理
                        case 3:
                            break;

                    }
                }
            }
            break;
    }


}

// 对动态图片进行处理
function pic_process(pictures, pic_div) {
    //当只有一张图片的时候就让图片的宽为534,高和宽同比缩放
    if (pictures.length === 1)
     {
        var pic_width = $(pic_div).width();
        var pic_height = pictures[0]["img_height"] * pic_width / pictures[0]["img_width"]
        var pic_url = pictures[0]["img_src"]
        //通过增加后缀减小图片的size
        pic_url = pic_url + "@" + Math.ceil(pic_width) + "w_" + Math.ceil(pic_height) + "h_1e_1c.webp"
        //通过图片的宽同比缩放图片的高

        pic_width = pic_width.toString() + "px"
        pic_height = pic_height.toString() + "px"
        $(pic_div).append("<img src='" + pic_url + "' class='single-pic'>")
        $(".single-pic").css({ "width": pic_width, "height": pic_height })

    }
    else if (pictures.length > 1 && pictures.length < 4)
     {
        //当图片大于一张小于四张的时候,图片所在的div宽高为534的n分之一
        for (i = 0; i < pictures.length; i++) {
            //每个图片所在的div的class—name
            var class_name = 'pic-mini-' + i
            //每个图片所在的div的selector
            var class_selector = "." + class_name
            //设置每个图片所在的div的大小
            var div_size = 513 / pictures.length
            //向DOM中添加装图片的div
            $(pic_div).append("<div class='pic-mini " + class_name + "'></div>")
            var vessel = $(class_selector)
            //图片的url
            pic_url = pictures[i]["img_src"]
            //通过增加后缀改变图片的size以达到加快渲染速度的目的
            if (pictures[i]["img_height"] > div_size)
            {
                pic_url = pic_url + "@" + Math.ceil(div_size) + "w_" + Math.ceil(div_size) + "h_1e_1c.webp"

            }
            else
            {
                pic_url = pic_url + "@" + Math.ceil(div_size) + "w_" + Math.ceil(div_size) + "h_!header.webp"

            }
            //给div设置宽高,以及将图片设为div的背景图片
            vessel.css({
                "width": div_size.toString() + "px",
                "height": div_size.toString() + "px",
                "background-image": "url('" + pic_url + "')",
            })
        }
    }
    else if (pictures.length === 4)
    {
        for (i = 0; i < pictures.length; i++) {
            class_name = 'pic-mini-' + i
            class_selector = "." + class_name
            div_size = 513 / 2
            $(pic_div).append("<div class='pic-mini " + class_name + "'></div>")
            vessel = $(class_selector)
            pic_url = pictures[i]["img_src"]
            if (pictures[i]["img_height"] > div_size)
            {
                pic_url = pic_url + "@" + Math.ceil(div_size) + "w_" + Math.ceil(div_size) + "h_1e_1c.webp"

            }
            else
             {
                pic_url = pic_url + "@" + Math.ceil(div_size) + "w_" + Math.ceil(div_size) + "h_!header.webp"

            }
            vessel.css({
                "width": div_size.toString() + "px",
                "height": div_size.toString() + "px",
                "background-image": "url('" + pic_url + "')",
            })
        }
    }
    else
    {
        for (i = 0; i < pictures.length; i++) {
            class_name = 'pic-mini-' + i
            class_selector = "." + class_name
            div_size = 513 / 3
            $(pic_div).append("<div class='pic-mini " + class_name + "'></div>")
            vessel = $(class_selector)
            pic_url = pictures[i]["img_src"]
            if (pictures[i]["img_height"] > div_size)
            {
                pic_url = pic_url + "@" + Math.ceil(div_size) + "w_" + Math.ceil(div_size) + "h_1e_1c.webp"

            } else
            {
                pic_url = pic_url + "@" + Math.ceil(div_size) + "w_" + Math.ceil(div_size) + "h_!header.webp"

            }
            vessel.css({
                "width": div_size.toString() + "px",
                "height": div_size.toString() + "px",
                "background-image": "url('" + pic_url + "')",
            })
        }
    }
}

function music_process(cards, type) {
    var music_cover;
    var title;
    var typeInfo;
    switch (type) {
        case 0:
            $(".music").css("display", "block")
            music_cover = cards.cover;
            title = cards.title;
            typeInfo = cards.typeInfo;
            $(".music-cover").css({ "background-image": "url('" + music_cover + "')" })
            $(".music-title").text(title)
            $(".music-desc").text(typeInfo)
            break;
        case 1:
            $(".repost-music").css("display", "block")
            music_cover = cards.cover;
            title = cards.title;
            typeInfo = cards.typeInfo;
            $(".repost-music-cover").css({ "background-image": "url('" + music_cover + "')" })
            $(".repost-music-title").text(title)
            $(".repost-music-desc").text(typeInfo)
            break;



    }

}

//对影视进行处理
function movie(type) {
    var pic_url
    var title
    var button
    switch (type) {
        case 4098:
            $(".movie").css("display", "block");
            pic_url = JSON.parse(JSON.parse(card.card).origin).cover + "@203w_127h_1e_1c.webp";
            title = JSON.parse(JSON.parse(card.card).origin).apiSeasonInfo.title;
            button = JSON.parse(JSON.parse(card.card).origin).apiSeasonInfo.type_name;
            $(".repost-movie-cover").css({ "background-image": "url('" + pic_url + "')" });
            $(".repost-movie-title").text(title);
            $(".repost-movie-button").text(button)
            break;
        case 4099:
        case 4101:
        case 512:
            $(".movie").css("display", "block")
            pic_url = JSON.parse(JSON.parse(card.card).origin).cover + "@203w_127h_1e_1c.webp";
            title = JSON.parse(JSON.parse(card.card).origin).new_desc;
            button = JSON.parse(JSON.parse(card.card).origin).apiSeasonInfo.type_name;
            $(".repost-movie-cover").css({ "background-image": "url('" + pic_url + "')" });
            $(".repost-movie-title").text(title);
            $(".repost-movie-button").text(button)
            break;

    }


}


function other_process(card, type) {
    var cover_url;
    var desc_text;
    var title;
    switch (type) {
        case 0:
            cover_url = card.sketch.cover_url;
            desc_text = card.sketch.desc_text;
            title = card.sketch.title;
            switch (card.sketch.biz_type) {
                //装扮
                case 3:
                    $(".decorate").css("display", "block");
                    $(".decorate-cover").css({ "background-image": "url('" + cover_url + "')" });
                    $(".decorate-title").text(title)
                    $(".decorate-desc").text(desc_text)
                    break;
                //挂件 
                case 231:
                    console.log(3);
                    $(".primp").css("display", "block");
                    $(".primp-cover").css({ "background-image": "url('" + cover_url + "')" });
                    $(".primp-title").text(title)
                    $(".primp-desc").text(desc_text)
                    break;
                //歌单
                case 131:
                    $(".playlist").css("display", "block");
                    $(".playlist-cover").css({ "background-image": "url('" + cover_url + "')" });
                    $(".playlist-title").text(title)
                    $(".playlist-desc").text(desc_text)
                    break;
                //漫画
                case 201:
                    $(".comic").css("display", "block");
                    $(".comic-title").text(title);
                    $(".comic-desc-fist").text(desc_text)
                    $(".comic-desc-second").text(card.sketch.text)
                    $(".comic-cover").css({ "background-image": "url('" + cover_url + "')" });
                    break;
            }

        case 1:
            console.log(1);
            cover_url = JSON.parse(card.origin).sketch.cover_url;
            desc_text = JSON.parse(card.origin).sketch.desc_text;
            title = JSON.parse(card.origin).sketch.title;
            switch (JSON.parse(card.origin).sketch.biz_type) {
                //装扮
                case 3:
                    $(".repost-decorate").css("display", "block");
                    $(".repost-decorate-cover").css({ "background-image": "url('" + cover_url + "')" });
                    $(".repost-decorate-title").text(title)
                    $(".repost-decorate-desc").text(desc_text)
                    break;
                //挂件 
                case 231:
                    console.log(3);
                    $(".repost-primp").css("display", "block");
                    $(".repost-primp-cover").css({ "background-image": "url('" + cover_url + "')" });
                    $(".repost-primp-title").text(title)
                    $(".repost-primp-desc").text(desc_text)
                    break;
                //歌单
                case 131:
                    $(".repost-playlist").css("display", "block");
                    $(".repost-playlist-cover").css({ "background-image": "url('" + cover_url + "')" });
                    $(".repost-playlist-title").text(title)
                    $(".repost-playlist-desc").text(desc_text)
                    break;
                //漫画
                case 201:
                    $(".repost-comic").css("display", "block");
                    $(".repost-comic-title").text(title);
                    $(".repost-comic-desc-fist").text(desc_text)
                    $(".repost-comic-desc-second").text(JSON.parse(card.origin).sketch.text)
                    $(".repost-comic-cover").css({ "background-image": "url('" + cover_url + "')" });
                    break;

            }


    }
}

// 对投稿视频进行处理
function video_process(card, type) {
    var desc;
    var title;
    var pic_url;
    switch (type) {

        case 0:
            $(".video-info").css("display", "block")
            desc = JSON.parse(card.card).desc;
            title = JSON.parse(card.card).title;
            pic_url = JSON.parse(card.card).pic + "@203w_127h_1e_1c.webp";
            $(".video-cover").css({ "background-image": "url('" + pic_url + "')" });
            $(".video-title").text(title);
            $(".video-desc").text(desc);
            break;
        case 1:
            $(".repost-video").css("display", "block")
            pic_url = JSON.parse(JSON.parse(card.card).origin).pic + "@203w_127h_1e_1c.webp";
            desc = JSON.parse(JSON.parse(card.card).origin).desc;
            title = JSON.parse(JSON.parse(card.card).origin).title;
            $(".repost-video-cover").css({ "background-image": "url('" + pic_url + "')" });
            $(".repost-video-title").text(title);
            $(".repost-video-desc").text(desc)

    }


}

//对直播内容进行处理
function live_process(type) {
    var cover_url;
    var live_title;
    var live_desc
    $(".repost-live").css("display","block");
    switch (type) {
        case 4200:
            cover_url = JSON.parse(JSON.parse(card.card).origin).cover + "@203w_127h_1e_1c.webp";
            live_title = JSON.parse(JSON.parse(card.card).origin).title;
            live_desc = JSON.parse(JSON.parse(card.card).origin).area_v2_name +"&nbsp;&bull;&nbsp;" + JSON.parse(JSON.parse(card.card).origin).online+"人气";
            $(".repost-live-cover").css({ "background-image": "url('" + cover_url + "')" });
            $(".repost-live-title").text(live_title)
            $(".repost-live-desc").html(live_desc)
            break;
        case 4308:
            cover_url = JSON.parse(JSON.parse(card.card).origin).live_play_info.cover + "@203w_127h_1e_1c.webp";
            live_title = JSON.parse(JSON.parse(card.card).origin).live_play_info.title;
            live_desc = JSON.parse(JSON.parse(card.card).origin).live_play_info.area_name +"&nbsp;&bull;&nbsp;" + JSON.parse(JSON.parse(card.card).origin).live_play_info.online+"人气";
            $(".repost-live-cover").css({ "background-image": "url('" + cover_url + "')" });
            $(".repost-live-title").text(live_title)
            $(".repost-live-desc").html(live_desc)
            break;
        case 4302:
            cover_url = JSON.parse(JSON.parse(card.card).origin).cover + "@203w_127h_1e_1c.webp";
            live_title = JSON.parse(JSON.parse(card.card).origin).title;
            live_desc = JSON.parse(JSON.parse(card.card).origin).subtitle
            $(".repost-live-cover").css({ "background-image": "url('" + cover_url + "')" });
            $(".repost-live-title").text(live_title)
            $(".repost-live-desc").html(live_desc)
            $(".repost-live-button").text("付费课程")
            $(".repost-live-desc").css("margin-top","55px")
            break;
    }
    
}

//对动态的文字进行处理
function dynamic_text_process(d_type, info, type, tag) {
    // 先找到动态的文字
    var description = find_desc(d_type, info)
    // 如果有文字的话
    if (description !== undefined) {
        // 先找到文字中的at其他人的文字
        var ctrl = find_ctrl(d_type, info);
        // 找到topic文字
        var topic_list = find_topic(card, type);
        // 找到emoji文字，类似于[微笑]这种的
        var emoji_list = find_emoji(card, type);
        // 找到文字中的富文本内容
        var richtext_list = find_rich_text(card, type)
        // 先把动态的文字中的空格换为㊟，如果直接将空格换为&nbsp;的话文本的总字数就变了，之后就不好换at那一部分了
        while (description.indexOf(" ") !== -1) {
            description = description.replace(" ", "㊟");
        }
        // 如果文本中有at其他人，就将at的部分换成蓝色的文字
        if (ctrl !== undefined) {
            description = at_process(description, ctrl);
        }
        // 如果动态文本中有topic就把topic换成蓝色的文本
        if (topic_list !== undefined) {
            description = topic_process(description, topic_list);
        }
        // 如果动态文本中有emoji的话就将[微笑]换成对应的图片的链接
        if (emoji_list !== undefined) {
            description = emoji_process(description, emoji_list);
        }
        // 如果有富文本，就将其从源文本，换成对应样式
        if (richtext_list !== undefined) {
            description = richtext_process(description, richtext_list);
        }
        // 将换行符换成html的换行符
        while (description.indexOf("\n") !== -1) {
            description = description.replace("\n", "<br>");
        }
        // 将㊟换成html的空格
        while (description.indexOf("㊟") !== -1) {
            description = description.replace("㊟", "&nbsp;");
        }
        // 将文本中的B站链接换成对应样式
        description = httpString(description)
        $(tag).html(description);
    }
}

// 对专栏进行处理
function article_process(card, type) {
    var img_url;
    //专栏标题
    var title;
    //专栏简介
    var summary;

    switch (type) {
        // 0是自己发的，1是转发的
        case 0:
            $(".article").css("display", "block");
            //专栏的封面图的url
            img_url = card.image_urls[0] + "@520w_120h_1e_1c.webp";
            //专栏标题
            title = card.title;
            //专栏简介
            summary = card.summary;
            $(".article-cover").css({ "background-image": "url('" + img_url + "')" });
            $(".article-title").text(title);
            $(".article-desc").text(summary);
            break;
        case 1:
            console.log(JSON.parse(card));
            $(".repost-article").css("display", "block");
            //专栏的封面图的url
            img_url = JSON.parse(card).image_urls[0] + "@520w_120h_1e_1c.webp"
            //专栏标题
            title = JSON.parse(card).title
            //专栏简介
            summary = JSON.parse(card).summary
            $(".repost-article-cover").css({ "background-image": "url('" + img_url + "')" });
            $(".repost-article-title").text(title);
            $(".repost-article-desc").text(summary);
            break;
    }
}


function repost_info_process(type) {
    var origin_face
    var origin_name
    switch (type) {
        default:
            origin_face = JSON.parse(card.card).origin_user.info.face;
            origin_name = JSON.parse(card.card).origin_user.info.uname;
            $(".oringin-face").css({ "background-image": "url('" + origin_face + "@24w_24h.webp" + "')", });
            $(".oringin-uname").text(origin_name);
            break;
        //电影
        case 4099:
        //番剧
        case 512:
        //专栏
        case 4101:
        //电视剧
        case 4098:
            origin_face = JSON.parse(JSON.parse(card.card).origin).apiSeasonInfo.cover;
            origin_name = JSON.parse(JSON.parse(card.card).origin).apiSeasonInfo.title;
            $(".oringin-face").css({ "background-image": "url('" + origin_face + "@24w_24h.webp" + "')", });
            $(".oringin-uname").text(origin_name);
            break;
        case 4302:
            origin_face = JSON.parse(JSON.parse(card.card).origin).up_info.avatar;
            origin_name = JSON.parse(JSON.parse(card.card).origin).up_info.name;
            $(".oringin-face").css({ "background-image": "url('" + origin_face + "@24w_24h.webp" + "')", });
            $(".oringin-uname").text(origin_name);
    }

}

// 对投票内容进行处理
function vote_process(type, content, c_type) {
    var ctrl = find_ctrl(type, content)
    if (ctrl !== undefined) {
        if (ctrl.some(item => item.type === 3)) {
            var vote_title
            var vote_desc
            switch (c_type) {
                case 0:
                    vote_title = card.extension.vote_cfg.desc;
                    desc = card.extension.vote_cfg.join_num;
                    $(".vote-info").css("display", "block");
                    $(".vote-title").text(vote_title);
                    $(".vote-desc").text(desc + "人参与");
                    break;
                case 1:
                    vote_title = JSON.parse(card.card).origin_extension.vote_cfg.desc
                    desc = JSON.parse(card.card).origin_extension.vote_cfg.join_num;
                    console.log(JSON.parse(card.card));
                    $(".repost-vote-info").css("display", "block");
                    $(".repost-vote-title").text(vote_title);
                    $(".repost-vote-desc").text(desc + "人参与");
            }
        }
    }
}


function repost_process() {
    repost_info_process(card.desc.orig_type);
    dynamic_text_process(card.desc.orig_type, JSON.parse(JSON.parse(card.card).origin), 1, ".repost-text")
    add_on_card_info(card, 1)
    var content_tag = $(".repost")
    switch (card.desc.orig_type) {
        //带图片的动态
        case 2:
            pic_process(JSON.parse(JSON.parse(card.card).origin).item.pictures, ".repost-pic");
            content_tag.css("height", (content_tag.height() + 10) + "px");
            break;
        //纯文字动态
        case 4:
            vote_process(card.desc.orig_type, JSON.parse(JSON.parse(card.card).origin), 1);
            content_tag.css("height", (content_tag.height() + 10) + "px")
            break;
        //投稿视频
        case 8:
            video_process(card, 1);
            content_tag.css("height", (content_tag.height() + 10) + "px")
            break;
        //专栏
        case 64:
            article_process(JSON.parse(card.card).origin, 1);
            content_tag.css("height", (content_tag.height() + 10) + "px");
            break;
        //音频
        case 256:
            music_process(JSON.parse(JSON.parse(card.card).origin), 1);
            content_tag.css("height", (content_tag.height() + 10) + "px");
            break;
        //转发挂件
        case 2048:
        //转发漫画 未完成
        case 2049:
            other_process(JSON.parse(card.card), 1);
            content_tag.css("height", (content_tag.height() + 10) + "px");
            break;
        //转发电视剧
        //番剧
        case 512:
        //电视剧
        case 4099:
        //电影
        case 4098:
        //纪录片
        case 4101:
            movie(card.desc.orig_type);
            content_tag.css("height", (content_tag.height() + 10) + "px");
            break;
        //转发直播
        case 4200:
        case 4308:
        case 4302:
            live_process(card.desc.orig_type)
            content_tag.css("height", (content_tag.height() + 10) + "px");
            break;


    }
}

//
//function main(card) {
//    //先设置一下头像,昵称,时间,二维码,认证图标
//    user_info_process(card);
//    //对文字内容进行处理
//    dynamic_text_process(card.desc.type, JSON.parse(card.card), 0, ".dynamic-text");
//    add_on_card_info(card, 0);
//    //找出转发内容所在的div,因为这个div背景颜色和其他的div不太一样
//    //这个div的默认display为none,当动态类型为转发的时候将其display改为block
//    var repost = $(".repost");
//    switch (card.desc.type) {
//        //转发的动态
//        case 1:
//            //对转发部分进行处理
//            //先让转发内容所在的div显示出来
//            repost.css("display", "block")
//            repost_process()
//            break;
//        //发送了一条带图片的动态
//        case 2:
//            //对图片进行处理
//            pic_process(JSON.parse(card.card).item.pictures, ".dynamic-pic");
//            break
//        //发送了一条纯文字动态
//        case 4:
//            //可能有投票,也可能有其他东西,但是只见过投票所以其他的以后有时间再加
//            vote_process(card.desc.type, JSON.parse(card.card), 0)
//            break
//        //发送了新投稿视频
//        case 8:
//            video_process(card, 0);
//            break;
//        //发送了专栏
//        case 64:
//            //对专栏进行处理
//            article_process(JSON.parse(card.card), 0);
//            break;
//        //音乐
//        case 256:
//            music_process(JSON.parse(card.card), 0)
//            break;
//        //挂件
//        case 2048:
//        //漫画
//        case 2049:
//            other_process(JSON.parse(card.card), 0);
//            break;
//    }
//}
//
//main()



