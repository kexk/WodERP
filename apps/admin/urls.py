#coding: utf-8

from __future__ import unicode_literals
from apps.admin.views import *
urls = [
    (r"", AdminHandler),
    (r'reg', RegHandler),
    (r'login', LoginHandler),
    (r'logout', LogoutHandler),
    (r'upload/', UploadHandler),
]