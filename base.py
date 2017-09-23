#coding:utf-8

import tornado.web

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