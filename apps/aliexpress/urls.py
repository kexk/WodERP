#coding: utf-8

from __future__ import unicode_literals
from apps.aliexpress.views import *
urls = [
    (r"orderList$", SMTOrderListHandler),
    (r"api/checkOrder$", SMTCheckOrderHandler),
    (r"api/refreshOrderStatus$", SMTRefreshOrderStatusHandler),
    (r"api/refreshOrderInfos$", SMTRefreshOrderInfosHandler),
]