#coding: utf-8

from __future__ import unicode_literals
from apps.aliexpress.views import *
urls = [
    (r"orderList$", SMTOrderListHandler),
    (r"orderList/v2$", SMTOrderListHandlerV2),
    (r"orderMergeList$", SMTOrderMergeHandler),
    (r"orderManager$", SMTOrderManagerHandler),
    (r"productList$", SMTProductListHandler),
    (r"api/checkOrder$", SMTCheckOrderHandler),
    (r"api/checkNewOrder$", SMTCheckNewOrderHandler),
    (r"api/refreshOrderStatus$", SMTRefreshOrderStatusHandler),
    (r"api/refreshOrderInfos$", SMTRefreshOrderInfosHandler),
    (r"api/checkProduct$", SMTCheckProductHandler),
    (r"api/refreshProductStatus$", SMTRefreshProductStatusHandler),
    (r"api/refreshProductInfos$", SMTRefreshProductInfosHandler),
    (r"api/refreshNewProductInfos$", SMTRefreshNewProductInfosHandler),
]