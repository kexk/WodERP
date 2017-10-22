#coding: utf-8

from __future__ import unicode_literals
from apps.aliexpress.views import *
urls = [
    (r"orderList$", SMTOrderListHandler),
    (r"productList$", SMTProductListHandler),
    (r"api/checkOrder$", SMTCheckOrderHandler),
    (r"api/refreshOrderStatus$", SMTRefreshOrderStatusHandler),
    (r"api/refreshOrderInfos$", SMTRefreshOrderInfosHandler),
    (r"api/checkProduct$", SMTCheckProductHandler),
    (r"api/refreshProductStatus$", SMTRefreshProductStatusHandler),
    (r"api/refreshProductInfos$", SMTRefreshProductInfosHandler),
]