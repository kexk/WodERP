#coding:utf-8

import falcon
import json

from webapi.falconApi import *

app = falcon.API()

app.req_options.auto_parse_form_urlencoded = True
app.req_options.keep_blank_qs_values = True


home = Home()
checkSMTOrder = CheckSMTOrder()
chekSMTProduct = ChekSMTProduct()
refreshSMTOrderStatus = RefreshSMTOrderStatus()
refreshSMTOrderInfos = RefreshSMTOrderInfos()
checkSMTNewOrderInfos = CheckSMTNewOrderInfos()
refreshSMTProductStatus = RefreshSMTProductStatus()
refreshSMTProductInfos = RefreshSMTProductInfos()
refreshSMTNewProductInfos = RefreshSMTNewProductInfos()
updateProductCategory = UpdateSMTProductCategory()
getAllProductCategory = GetAllProductCategory()
checkJDOrder = CheckJDOrder()
checkPurchaseOrder = CheckPurchaseOrder()

app.add_route('/',home)
app.add_route('/smt/api/checkOrder',checkSMTOrder)
app.add_route('/smt/api/checkProduct',chekSMTProduct)
app.add_route('/smt/api/refreshOrderStatus',refreshSMTOrderStatus)
app.add_route('/smt/api/refreshOrderInfos',refreshSMTOrderInfos)
app.add_route('/smt/api/checkNewOrder',checkSMTNewOrderInfos)
app.add_route('/smt/api/refreshProductStatus',refreshSMTProductStatus)
app.add_route('/smt/api/refreshProductInfos',refreshSMTProductInfos)
app.add_route('/smt/api/refreshNewProductInfos',refreshSMTNewProductInfos)
app.add_route('/smt/api/updateProductCategory',updateProductCategory)
app.add_route('/smt/api/getAllProductCategory',getAllProductCategory)
app.add_route('/jd/api/checkOrder',checkJDOrder)
app.add_route('/purchase/api/checkPurchase',checkPurchaseOrder)


if __name__ == '__main__':
    from waitress import serve
    serve(app, listen='0.0.0.0:5000')