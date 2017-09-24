#coding:utf-8
import os.path
import re

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
from tornado.options import define, options


from comm.jingdong.web import *
from comm.aliexpress.web import *
from comm.alibaba.web import *



define("port", default=9999, help="run on the given port", type=int)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("email")

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('error/404.html')
        elif status_code == 500:
            self.render('error/500.html')
        else:
            self.write('error:' + str(status_code))


class IndexHandler(BaseHandler):

    #@tornado.web.authenticated
    def get(self):
        greeting = self.get_argument('greeting', 'Hello')
        greeting += ', friendly user! '


        user = self.current_user
        role = self.get_secure_cookie("role") if self.get_secure_cookie("role") else 'None'


        self.render('index.html',greeting=greeting,userInfo={'account':user,'role':role})

        #self.render('index.html')

    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error.\n" % status_code)


class LoginHandler(BaseHandler):

    def get(self):
        user = self.current_user
        referer = self.get_argument('next','/')
        if user:
            self.redirect(referer)
        else:
            self.render('login.html',referer=referer)


    def post(self):

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
                            self.redirect(self.get_argument('next','/'))
                    else:
                        self.render('error.html',msg=u'未激活用户,重新申请激活 '+u'>> <a href="/profile">修改资料</a>')


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("email")
        self.clear_cookie("role")
        self.redirect('/')


class AuthHandler(BaseHandler):
    def get(self):
        code = self.get_argument('code', '')

        self.render('index.html')



if __name__ == "__main__":
    tornado.options.parse_command_line()
    settings = {
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "xsrf_cookies": True,
        'login_url':'/login'
    }
    app = tornado.web.Application(
        handlers=[(r"/", IndexHandler),
                  (r'/login', LoginHandler),
                  (r'/logout', LogoutHandler),
                  (r"/jd/orderList$", JDOrderListHandler),
                  (r"/purchaseList$", PurchaseListHandler),
                  (r"/smt/api/checkOrder$", CheckSmtOrderHandler),
                  (r"/jd/api/checkOrder$", JDCheckOrderHandler),
                  (r"/jd/api/checkOrderInfo$", JDChcekOrderInfoHanlder),
                  (r"/jd/api/getSkuImage$", GetJdSkuImageHandler),
                  (r"/jd/api/checkSku$", JDCheckSkuHandler),
                  (r"/alibaba/api/getPurchaseInfo$", getPurchaseInfoHandler),
                  (r"/alibaba/api/checkPurchase$", CheckPurchaseHandler),
                  (r"/alibaba/api/checkPurchaseInfo$", CheckPurchaseInfoHandler),
                  (r"/alibaba/api/checkPurchaseLogist$", CheckPurchaseLogistHandler),
                  (r"/jd/api/matchPurchaseOrder$", JdMatchPurchaseOrderHandler),
                  (r".*", BaseHandler),
                  ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True,
        **settings
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    #http_server.bind(options.port)
    #http_server.start(num_processes=0)
    tornado.ioloop.IOLoop.instance().start()