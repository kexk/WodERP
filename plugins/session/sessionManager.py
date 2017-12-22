#coding:utf-8
## --------------------------------------------
  
# session manager

import time
import os
from hashlib import sha1
  
class SessionManagerBase(object):  
    """session manager的基类"""  
    def generate_session_id(self, salt):  
        """生成唯一的session_id"""  
        rand = os.urandom(16)  
        now = time.time()  
        return sha1("%s%s%s" %(rand, now, salt)).hexdigest()  
  
    def create_new(self, session_id):  
        """创建空session，当session不存在时"""  
        pass  
  
    def save_session(self, session):  
        """保存session"""  
        pass  
  
    def load_session(self, session_id = None):  
        """根据session_id load session"""  
        pass  
  
  
## --------------------------------------------  
  
class MongoSessionManager(SessionManagerBase):  
    def __init__(self, db, collection_name='sessions', **kw):  
        """session 采用mongodb为后端保存， 默认是存在 sessions 集合中"""  
        self._collection = db[collection_name]  
  
    def create_new(self, session_id):  
        return BaseSession(session_id, self, {})  
  
    def save_session(self, session):  
        """保存session 到mongodb"""  
        self._collection.save({'_id' : session.get_session_id(), 'data' : session})  
  
    def load_session(self, session_id = None):  
        data = {} # 默认为空session  
        if session_id:  
            # 有session ，就调入  
            session_data = self._collection.find_one({'_id' : session_id})  
            if session_data:  
                # 防止错误数据  
                data = session_data['data']  
  
        return BaseSession(session_id, self, data)  
  
## --------------------------------------------  
# session  
  
class BaseSession(dict):
    def __init__(self, session_id = '', mgr = None, data = {}):  
        self.__session_id = session_id  
        self.__mgr = mgr  
        self.update(data)  
        self.__change = False # 小小的优化， 如果session没有改变， 就不用保存了  
  
    def get_session_id(self):  
        return self.__session_id  
    
    def save(self):  
        if self.__change:  
            self.__mgr.save_session(self)  
            self.__change = False  
  
    # ------------------------------------------  
    # 使用session[key] 当key不存在时返回None， 防止出现异常  
    def __missing__(self, key):  
        return None  
  
    def __delitem__(self, key):  
        if key in self:  
            del self[key]  
            self.__change = True  
  
    def __setitem__(self, key, val):  
        self.__change = True  
        super(BaseSession, self).__setitem__(key, val)  