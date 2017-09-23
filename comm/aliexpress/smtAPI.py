#coding:utf-8


import requests
import datetime


class ALIEXPRESS:

    appKey = ''
    apiRoot = ''

    def __init__(self,appKey,apiRoot):
        self.appKey = appKey
        self.apiRoot = apiRoot


    def getOrderDetail(self,orderId,fieldList='',extInfoBitFlag=''):

        apiPath = 'api.findOrderById'


        data = {'orderId':orderId,'apiPath':apiPath,'appKey':self.appKey,'fieldList':fieldList,'extInfoBitFlag':extInfoBitFlag}

        r = requests.post(self.apiRoot,data=data)
        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''



    def getOrderList(self,option={}):

        apiPath = 'api.findOrderListQuery'

        data = {'appKey':self.appKey,'apiPath':apiPath,'orderStatus':'','page':'1','pageSize':'20','createDateStart':'','createDateEnd':''}

        for (k,v) in  option.items():
            data[k] = v


        r = requests.post(self.apiRoot,data=data)


        if r.status_code == 200:
            return r.content
        else:
            return '''{"result:{"success":false}}'''







