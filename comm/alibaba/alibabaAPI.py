#coding:utf-8


import requests
import datetime


class ALIBABA:

    appKey = ''
    memberId = ''
    apiRoot = ''


    def getOrderDetail(self,orderId):

        urlPath = 'param2/2/cn.alibaba.open/trade.order.orderDetail.get/'


        data = {'orderId':orderId,'urlPath':urlPath,'appKey':self.appKey}

        r = requests.post(self.apiRoot,data=data)
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


        r = requests.post(self.apiRoot,data=data)


        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''







