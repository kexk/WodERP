#coding:utf-8


import requests
import datetime
import json


class ALIBABA:

    appKey = ''
    memberId = ''
    apiRoot = ''
    apiRoute = 'requestAPI.php'

    def __init__(self,app):
        self.appKey = app['appKey']
        self.apiRoot = app['apiRoot']
        self.memberId = app['memberId']


    #订单详情查看(买家视角)
    def getOrderDetailBuyerView(self,orderId,webSite='1688',includeFields=''):
        urlPath = 'param2/1/com.alibaba.trade/alibaba.trade.get.buyerView/'

        data = {'urlPath':urlPath,'appKey':self.appKey,'orderId':orderId,'webSite':webSite,'includeFields':includeFields}

        r = requests.post(self.apiRoot+self.apiRoute,data=data)
        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''

    #订单列表查看(买家视角)
    def getBuyerOrderList(self,option={}):
        urlPath = 'param2/1/cn.alibaba.open/trade.order.orderList.get/'

        data = {'appKey':self.appKey,'urlPath':urlPath,'sellerMemberId':'','sellerRateStatus':'','tradeType':'','bizTypes':json.dumps(["cn","ws"]),'orderStatus':'','refundStatus':'','page':'1','pageSize':'20','isHis':'false',
        'createStartTime':datetime.datetime.now().strftime('%Y-%m-%d')+' 00:00:00','createEndTime':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'modifyStartTime':'',
        'modifyEndTime':''}

        for (k,v) in  option.items():
            data[k] = v


        r = requests.post(self.apiRoot+self.apiRoute,data=data)


        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''



    def getOrderDetail(self,orderId):

        urlPath = 'param2/2/cn.alibaba.open/trade.order.orderDetail.get/'


        data = {'orderId':orderId,'urlPath':urlPath,'appKey':self.appKey}

        r = requests.post(self.apiRoot+self.apiRoute,data=data)
        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''



    def getOrderList(self,option={}):

        urlPath = 'param2/1/cn.alibaba.open/trade.order.orderList.get/'

        data = {'appKey':self.appKey,'buyerMemberId':self.memberId,'sellerMemberId':'','tradeType':'','orderStatus':'','pageNO':'1','pageSize':'20','isHis':'false','productName':'',
        'orderId':'','createStartTime':datetime.datetime.now().strftime('%Y-%m-%d')+' 00:00:00','createEndTime':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'modifyStartTime':'',
        'modifyEndTime':'','urlPath':urlPath}

        for (k,v) in  option.items():
            data[k] = v


        r = requests.post(self.apiRoot+self.apiRoute,data=data)


        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''


    #物流公司列表-所有的物流公司
    def getLogisticCompanyList(self):
        urlPath = 'param2/1/com.alibaba.logistics/alibaba.logistics.OpQueryLogisticCompanyList/'

        data = {'appKey':self.appKey,'urlPath':urlPath}

        r = requests.post(self.apiRoot+self.apiRoute,data=data)

        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''



    #获取交易订单的物流跟踪信息(买家视角)
    def getLogisticsTraceInfo(self,orderId,logisticsId='',webSite='1688'):
        urlPath = 'param2/1/com.alibaba.logistics/alibaba.trade.getLogisticsTraceInfo.buyerView/'

        data = {'appKey':self.appKey,'urlPath':urlPath,'orderId':orderId,
                'logisticsId':logisticsId,'webSite':webSite}

        r = requests.post(self.apiRoot+self.apiRoute,data=data)

        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''

    #获取交易订单的物流信息(买家视角)
    def getLogisticsInfos(self,orderId,fields='',webSite='1688'):
        urlPath = 'param2/1/com.alibaba.logistics/alibaba.trade.getLogisticsInfos.buyerView/'

        data = {'appKey':self.appKey,'urlPath':urlPath,'orderId':orderId,
                'fields':fields,'webSite':webSite}

        r = requests.post(self.apiRoot+self.apiRoute,data=data)

        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''

    # 获取非授权用户的商品
    def getProduct(self, productID, webSite='1688'):

        urlPath = 'param2/1/com.alibaba.product/alibaba.agent.product.get/'

        data = {'appKey': self.appKey, 'urlPath': urlPath, 'productID': productID, 'webSite': webSite}

        r = requests.post(self.apiRoot + self.apiRoute, data=data)

        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''


    # 支付单生成(网银支付方式)
    def createPayment(self, orderId):

        urlPath = 'param2/1/com.alibaba.trade/alibaba.payment.order.bank.create/'

        data = {'appKey': self.appKey, 'urlPath': urlPath, 'orderId': orderId}

        r = requests.post(self.apiRoot + self.apiRoute, data=data)

        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''

    def parseAddress(self,addressInfo):
        urlPath = 'param2/1/com.alibaba.trade/alibaba.trade.addresscode.parse/'

        data = {'appKey':self.appKey,'urlPath':urlPath,'addressInfo':addressInfo}

        r = requests.post(self.apiRoot+self.apiRoute,data=data)

        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''


    def createOrder(self,cargoGroups,otherInfoGroup,receiveAddressGroup,invoiceGroup={}):
        urlPath = 'param2/1/com.alibaba.trade/alibaba.trade.general.CreateOrder/'

        data = {'appKey':self.appKey,'urlPath':urlPath,'cargoGroups':json.dumps(cargoGroups),
                'otherInfoGroup':json.dumps(otherInfoGroup),'receiveAddressGroup':json.dumps(receiveAddressGroup),
                'invoiceGroup':json.dumps(invoiceGroup)}

        r = requests.post(self.apiRoot+self.apiRoute,data=data)

        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''

    #创建订单的预先浏览展示(通用大市场)
    def createPreorder(self,goods,receiveAddress,extension=[]):
        urlPath = 'param2/1/com.alibaba.trade/alibaba.trade.general.preorder/'

        data = {'appKey':self.appKey,'urlPath':urlPath,'goods':json.dumps(goods),
                'receiveAddress':json.dumps(receiveAddress),'extension':json.dumps(extension)}

        r = requests.post(self.apiRoot+self.apiRoute,data=data)

        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''


    def fastCreateOrder(self,addressParam,cargoParamList,flow='general',invoiceParam={},subUserId='',message=''):
        urlPath = 'param2/1/com.alibaba.trade/alibaba.trade.fastCreateOrder/'

        data = {'appKey':self.appKey,'urlPath':urlPath,'flow':flow,'cargoParamList':json.dumps(cargoParamList),
                'addressParam':json.dumps(addressParam),'invoiceParam':json.dumps(invoiceParam),
                'subUserId':subUserId,'message':message}

        r = requests.post(self.apiRoot+self.apiRoute,data=data)

        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''

