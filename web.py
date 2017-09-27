#coding:utf-8
import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
from tornado.options import define, options

from importlib import import_module


from apps.jingdong.views import *
from apps.aliexpress.views import *
from apps.alibaba.views import *



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



class AuthHandler(BaseHandler):
    def get(self):
        code = self.get_argument('code', '')

        self.render('index.html')



def include(module):
    res = import_module(module)
    urls = getattr(res, 'urls', res)
    return urls

def url_wrapper(urls):
    wrapper_list = []
    for url in urls:
        path, handles = url
        if isinstance(handles, (tuple, list)):
            for handle in handles:
                pattern, handle_class = handle
                wrap = ('{0}{1}'.format(path, pattern), handle_class)
                wrapper_list.append(wrap)
        else:
            wrapper_list.append((path, handles))
    return wrapper_list


if __name__ == "__main__":
    tornado.options.parse_command_line()
    settings = {
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "xsrf_cookies": True,
        'login_url':'/login'
    }
    app = tornado.web.Application(
        url_wrapper([
            (r"/", IndexHandler),
            (r"/jd/", include('apps.jingdong.urls')),
            (r"/smt/", include('apps.aliexpress.urls')),
            (r"/purchase/", include('apps.alibaba.urls')),
            (r"/admin/", include('apps.admin.urls')),
            (r".*", BaseHandler),
        ]),
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