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
        message = dict()
        message['Code'] = status_code
        message['Link'] = '/'
        if status_code == 404:
            message['Title'] = 'Page Not Found'
            message['Msg'] = '页面未找到'
            self.render('error/message.html', msg=message)
        elif status_code == 500:
            message['Title'] = 'Service Unavailable'
            message['Msg'] = '服务器内部错误'
            self.render('error/message.html', msg=message)
        else:
            #self.write('error:' + str(status_code))
            message['Title'] = 'Unknow Error '
            message['Msg'] = '未知错误'
            self.render('error/message.html',msg=message)
