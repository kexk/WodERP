#coding: utf-8

from __future__ import unicode_literals
from apps.jingdong.views import *
urls = [
    (r"orderList$", JDOrderListHandler),
    (r"api/checkOrder$", JDCheckOrderHandler),
    (r"api/checkOrderInfo$", JDChcekOrderInfoHanlder),
    (r"api/getSkuImage$", GetJdSkuImageHandler),
    (r"api/checkSku$", JDCheckSkuHandler),
    (r"api/matchPurchaseOrder$", JdMatchPurchaseOrderHandler),
]