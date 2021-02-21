import json
from datetime import datetime

import nonebot
from nonebot.adapters.cqhttp import MessageEvent
from tinydb import TinyDB, Query

from .utils import get_path
from .version import __version__
from packaging.version import Version


class Config():
    """操作 config.json 文件"""

    def __init__(self, event:MessageEvent=None):
        self._init(event)
    
    def __enter__(self, event:MessageEvent=None):
        self._init(event)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.config.close()
    
    def _init(self, event=None):
        self.config = TinyDB(get_path('config.json'), encoding='utf-8')
        self.uids = self.config.table('uids')
        self.groups = self.config.table('groups')
        self.uid_lists = self.config.table('uid_lists')
        self.login = self.config.table('login')
        self.version = self.config.table('version')

        if event:
            self.bot_id = str(event.self_id)
            self.type = event.message_type
            self.type_id = str(event.group_id) if self.type == 'group' else str(event.user_id)
    
    def uid_exist(self, uid, type_id=False):
        q = Query()
        if type_id:
            r = self.config.get((q.uid == uid) & (q.type == self.type) & (q.type_id == self.type_id))
        else:
            r = self.config.get((q.uid == uid))
        return r
    
    def add_admin(self):
        if self.type == 'private':
            return
        q = Query()
        if not self.groups.contains(q.group_id == self.type_id):
            self.groups.insert({'group_id': self.type_id, 'admin': True})

    def update_uid_lists(self):
        if 'uid_lists' not in self.config.tables():
            self.uid_lists.insert_multiple([
                {
                    'dynamic': [],
                    'index': 0
                },
                {
                    'live': [],
                    'index': 0
                }
            ])
        q = Query()
        r = self.config.search(q.dynamic == True)
        dynamic = list(set([c['uid'] for c in r]))
        self.uid_lists.update({'dynamic': dynamic}, q.dynamic.exists())
        r = self.config.search(q.live == True)
        live = list(set([c['uid'] for c in r]))
        self.uid_lists.update({'live': live}, q.live.exists())

    async def add_uid(self, uid):
        """添加主播"""
        
        r = self.uid_exist(uid, True)
        if r: # 已经存在
            return f"请勿重复添加 {r['name']}（{r['uid']}）"
        
        self.add_admin()
        r = self.uid_exist(uid)
        if r: # 当前账号没订阅，但是其他账号添加过这个 uid
            name = r['name']
        else: # 没有账号订阅过这个 uid
            from .bilireq import BiliReq
            br = BiliReq()
            try: # 检测 uid 是否有效（逻辑需要修改）
                user_info = await br.get_info(uid)
                name = user_info["name"]
            except:
                return "请输入有效的uid"
            
        self.config.insert({
            'uid': uid,
            'name': name,
            'type': self.type, 
            'type_id': self.type_id,
            'live': True,
            'dynamic': True,
            'at': False,
            'bot_id': self.bot_id
            })
        self.update_uid_lists()
        return f"已添加 {name}（{uid}）"
    
    async def delete_uid(self, uid):
        """删除主播"""

        r = self.uid_exist(uid, True)
        if not r:
            return "删除失败，uid 不存在"
        q = Query()
        self.config.remove(
            (q.uid == uid) & 
            (q.type == self.type) & 
            (q.type_id == self.type_id))
        self.update_uid_lists()
        return f"已删除 {r['name']}（{uid}）"
    
    async def delete_push_list(self):
        """删除指定对象的推送列表"""

        q = Query()
        self.config.remove(
            (q.type == self.type) &
            (q.type_id == self.type_id))
        self.update_uid_lists()

    async def uid_list(self):
        """主播列表"""

        q = Query()
        r = self.config.search((q.type == self.type) & (q.type_id == self.type_id))
        message = "以下为当前的订阅列表：\n\n"
        for c in r:
            message += (
                f"【{c['name']}】" +
                f"直播推送：{'开' if c['live'] else '关'}，" +
                f"动态推送：{'开' if c['dynamic'] else '关'}" +
                f"（{c['uid']}）\n"
            )
        return message

    async def set(self, func, uid, status):
        """开关各项功能"""

        if func == 'at' and self.type == 'private':
            return "只有群里才能name"

        r = self.uid_exist(uid, True)
        if not r:
            return "name失败，uid 不存在"
        
        if r[func] == status:
            return "请勿重复name"

        q = Query()
        self.config.update({func: status}, (q.uid == uid) & (q.type == self.type) & (q.type_id == self.type_id))
        self.update_uid_lists()
        return f"已name，{r['name']}（{r['uid']}）"

    async def set_permission(self, status):
        """设置权限"""

        if self.type == 'private':
            return "只有群里才能name"
        
        q = Query()
        r = self.groups.get(q.group_id == self.type_id)
        if (not r and status) or (r and r['admin'] == status):
            return "请勿重复name"
        if not self.groups.contains(q.group_id == self.type_id):
            self.groups.insert({'group_id': self.type_id, 'admin': status})
        else:
            self.groups.update({'admin': status}, q.group_id == self.type_id)
        return "已name，只有管理员才能使用" if status else "已name，所有人都能使用"

    def next_uid(self, func):
        """获取下一位爬取的 uid"""
        
        q = Query()
        r = self.uid_lists.get(q[func].exists())
        if not r: # 一次都没有添加过，uid_list 还没有创建
            return None
        index = r['index']
        uid_list = r[func]

        if not uid_list: # uid_list 为空
            return None
        
        if index >= len(uid_list):
            uid = uid_list[0]
            index = 1
        else:
            uid = uid_list[index]
            index += 1
        self.uid_lists.update({'index': index}, q[func].exists())
        return uid
    
    
    def get_uid_list(self, name):
        """获取需要爬取的 UID 列表"""

        q = Query()
        r = self.uid_lists.get(q[name].exists())
        if not r:
            return []
        return r[name]


    def get_push_list(self, uid, func):
        """获取推送列表"""

        q = Query()
        return self.config.search((q.uid == uid) & (q[func] == True))

    def get_admin(self, group_id):
        q = Query()
        if not self.groups.contains(q.group_id == group_id):
            return True
        return self.groups.get(q.group_id == group_id)['admin']

    @classmethod
    def get_name(cls, uid):
        """获取 uid 对应的昵称"""

        q = Query()
        return (cls().config.get(q.uid == str(uid)))['name']
    
    def read(self):
        """读取用户注册信息"""

        with open(get_path('config.json'), encoding='utf-8-sig') as f:
            text = f.read()
        self.json = json.loads(text)
        return self.json

    def backup(self):
        """备份当前配置文件"""

        # FIXME 如果 config.json 不存在，不备份
        self.read()
        backup_name = f"config.{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json.bak"
        with open(get_path(backup_name), 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.json, ensure_ascii=False, indent=4))
        return True
    
    @classmethod
    def get_login(cls):
        """获取登录信息"""

        if 'login' not in cls().config.tables():
            tokens = {
                'access_token': '',
                'refresh_token': ''
            }
            cls().login.insert(tokens)
        else:
            tokens = cls().login.all()[0]
        if tokens == {'access_token': '', 'refresh_token': ''}:
            return None
        return tokens

    @classmethod
    def update_login(cls, tokens):
        """更新登录信息"""

        cls().login.update({
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token']
        })

    def new_version(self):
        if 'version' not in self.config.tables():
            self.version.insert({'version': __version__})
            return True
        current_version = Version(__version__)
        old_version = Version(self.version.all()[0]['version'])
        return current_version > old_version
    
    def update_version(self):
        self.version.update({'version': __version__})
                

    @classmethod
    async def update_config(cls):
        """升级为 TinyDB"""

        with Config() as config:
            if 'status' in config.config.tables():
                config.backup()
                config.config.drop_tables()
                
                for c_type, config_type in {'group': 'groups', 'private': 'users'}.items():
                    config.type = c_type
                    for type_id, type_config in config.json[config_type].items():
                        config.type_id = type_id
                        uids = type_config['uid']
                        for uid, sets in uids.items():
                            config.bot_id = config.json['uid'][uid][config_type][config.type_id]
                            await config.add_uid(uid)
                            for func, status in sets.items():
                                await config.set(func, uid, status)
                        if 'admin' in type_config and not type_config['admin']:
                            await config.set_permission(False)
            if config.new_version():
                config.backup()
                config.update_version()


nonebot.get_driver().on_startup(Config.update_config)
