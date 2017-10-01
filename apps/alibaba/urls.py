#coding: utf-8

from __future__ import unicode_literals
from apps.alibaba.views import *
urls = [
    (r"", PurchaseListHandler),
    (r"api/getPurchaseInfo$", getPurchaseInfoHandler),
    (r"api/checkPurchase$", CheckPurchaseHandler),
    (r"api/checkPurchaseInfo$", CheckPurchaseInfoHandler),
    (r"api/checkPurchaseLogist$", CheckPurchaseLogistHandler),
    (r"api/parseAddress$", ParseAddressHandler),
]