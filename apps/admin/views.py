#coding:utf-8


from base import BaseHandler

import hashlib
import datetime
import os.path
import uuid
import tornado.web
from apps.database.databaseCase import *
from bson import ObjectId


class LoginHandler(BaseHandler):

    def get(self):
        homePath = self.getHome()
        user = self.current_user
        referer = self.get_argument('next',homePath)
        if user:
            self.redirect(referer)
        else:
            self.render('login.html',homePath=homePath,referer=referer)


    def post(self):

        homePath = self.getHome()

        email = self.get_argument('email','')
        password = self.get_argument('password','')

        if email == '' or password == '':
            self.render('error.html',msg=u'Email 密码 不能为空!')

        else:

            mongo = MongoCase()
            mongo.connect()
            client = mongo.client
            db = client.woderp
            user = db.user.find({"account":email})
            if user.count()<1:
                self.render('error.html',msg=u'Email 不存在')
            else:
                m = hashlib.md5()
                m.update(password)
                sign = m.hexdigest()
                if user[0]['password'] != sign:
                    self.render('error.html',msg=u'密码错误')

                else:
                    self.set_secure_cookie("email", email)
                    if user[0]['isSupper']:
                        self.set_secure_cookie("role", 'Admin')
                        #self.redirect('/admin')
                    else:
                        self.set_secure_cookie("role", 'User')

                    if user[0]['isActive']:
                            self.redirect(self.get_argument('next',homePath))
                    else:
                        self.render('error.html',homePath=homePath,msg=u'未激活用户,重新申请激活 '+u'>> <a href="/profile">修改资料</a>')


class LogoutHandler(BaseHandler,tornado.web.RequestHandler):
    def get(self):
        homePath = self.getHome()
        self.clear_cookie("email")
        self.clear_cookie("role")
        self.redirect(homePath)



class RegHandler(BaseHandler):

    def get(self):
        homePath = self.getHome()
        user = self.current_user
        referer = self.get_argument('referer',homePath)
        if user:
            self.redirect(referer)
        else:
            self.render('account/reg.html',homePath=homePath,referer=referer)

    def post(self):
        homePath = self.getHome()
        email = self.get_argument('email','')
        password = self.get_argument('password','')
        password_repeat = self.get_argument('password_repeat','')
        type = self.get_argument('type','1')
        if email == '' or '-' in email:
            self.render('error.html',msg=u'非法账号 不能为空、且不能含有[-]')

        elif password == '' or password_repeat =='':
            self.render('error.html',msg=u'密码不能为空，且要6-18位!')
        elif password != password_repeat:
            self.render('error.html',msg=u'密码不一致！')

        #查询
        else:
            mongo = MongoCase()
            mongo.connect()
            client = mongo.client
            db = client.woderp

            if db.user.find({"account":email}).count()>0:
                msg = email+u'已经注册过了'
                msg += u'<a href="/login">登录</a>'
                self.render('error.html',homePath=homePath,msg=msg)

            else:

                m = hashlib.md5()
                m.update(password)
                sign = m.hexdigest()
                item = {"account":email,"username":email, "password":sign,"regDate":datetime.datetime.now(),'status':'0','type':type,
                        "lastLoginDate":datetime.datetime.now(),"isActive":False,'isSupper':False}
                db.user.insert(item)

                self.set_secure_cookie("account", email)

                self.redirect(homePath)


class AuditUserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        homePath = self.getHome()
        user = user=self.current_user
        action = self.get_argument('action','')
        id = self.get_argument('id','')
        mongo = MongoCase()
        mongo.connect()
        client = mongo.client
        db = client.woderp
        userInfo = db.user.find({'account':user})
        if action != '' and id != ''and userInfo.count>0:
            if userInfo[0]['isSupper']:
                if action == 'delete':
                    db.user.remove({'_id':ObjectId(id)})
                    db.profile.remove({'_id':ObjectId(id)})
                elif action == 'deActive':
                    db.user.update({'_id':ObjectId(id)},{'$set':{'isActive':False,'status':1}})

                elif action == 'active':
                    db.user.update({'_id':ObjectId(id)},{'$set':{'isActive':True}})
                elif action == 'audit':
                    db.user.update({'_id':ObjectId(id)},{'$set':{'isActive':True,'status':2}})
                self.redirect(homePath+'admin/')
            else:
                self.render('error.html',homePath=homePath,msg=u'无权限删除！')
        else:
            self.render('error.html',homePath=homePath,msg=u'非法操作！')

class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        homePath = self.getHome()
        user = self.current_user
        mongo = MongoCase()
        mongo.connect()
        client = mongo.client
        db = client.woderp
        userInfo = db.user.find({"account":user})
        if user and userInfo.count():
            if userInfo[0]['isSupper']:
                userList = db.user.find({"isSupper":False})

                self.render('admin/admin.html',userList=userList,homePath=homePath,userInfo=userInfo[0])
            else:
                self.render('error/message.html',homePath=homePath,
                            msg={'Msg': 'No Permission', 'Code': 400, 'Title': '无权限！', 'Link': '/'})
        else:
            self.clear_cookie('account')
            self.render('error/message.html',homePath=homePath, msg={'Msg': 'No Permission', 'Code': 400, 'Title': '非法用户！', 'Link': '/'})

#文件上传（CKEditor使用）
class UploadHandler(BaseHandler):
    def post(self):
        homePath = self.getHome()
        imgfile = self.request.files.get('upload')
        callback = self.get_argument('CKEditorFuncNum')
        imgPath = []
        imgRoot = os.path.dirname(__file__)+'/static/woderp/uploads/'
        for img in imgfile:
            file_suffix = img['filename'].split(".")[-1]
            file_name=str(uuid.uuid1())+"."+file_suffix
            with open(imgRoot + file_name, 'wb') as f:
                f.write(img['body'])

            imgPath.append(file_name)

        self.write('<script type="text/javascript">window.parent.CKEDITOR.tools.callFunction('+callback+',"'+homePath+'static/woderp/uploads/'+imgPath[0]+'","")</script>')
