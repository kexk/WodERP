#coding:utf-8

import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("email")

    def getAuthority(self,account,AUTHOR_MOUDLE=None):

        authority = dict()

        if account == None:
            authority['role'] = 'Guest'
            authority['Allow'] = False
        elif account['isSupper']:
            authority['role'] = 'Supper'
            authority['authority'] = {}
            authority['Allow'] = True
        elif account.has_key('authority'):
            authority['role'] = 'User'
            authority['authority'] = account['authority']
            if AUTHOR_MOUDLE and authority['authority'].has_key('Permission') and AUTHOR_MOUDLE in authority['authority']['Permission']:
                authority['Allow'] = True
            else:
                authority['Allow'] = False
        else:
            authority['role'] = 'Guest'
            authority['authority'] = {}
            authority['Allow'] = False

        return authority

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('error/404.html')
        elif status_code == 500:
            self.render('error/500.html')
        else:
            #self.write('error:' + str(status_code))
            self.render('error.html',msg=status_code)
