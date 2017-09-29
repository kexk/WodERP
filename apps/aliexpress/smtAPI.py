#coding:utf-8


import requests


class ALIEXPRESS:

    appKey = ''
    apiRoot = ''
    apiRoute = 'requestAPI.php'

    def __init__(self,app):
        self.appKey = app['apiInfo']['appKey']
        self.apiRoot = app['apiInfo']['apiRoot']


    def getOrderDetail(self,orderId,fieldList='',extInfoBitFlag=''):

        apiPath = 'api.findOrderById'


        data = {'orderId':orderId,'apiPath':apiPath,'appKey':self.appKey,'fieldList':fieldList,'extInfoBitFlag':extInfoBitFlag}

        try:
            r = requests.post(self.apiRoot+self.apiRoute,data=data)
            if r.status_code == 200:
                return r.content
            else:
                return '''{"result:{"success":false}}'''
        except Exception as e:
            return '''{"result:{"success":false,"msg":"%s"}}''' % str(e)


    def getOrderList(self,option={}):

        apiPath = 'api.findOrderListQuery'

        data = {'appKey':self.appKey,'apiPath':apiPath,'orderStatus':'','page':'1','pageSize':'20','createDateStart':'','createDateEnd':''}

        for (k,v) in  option.items():
            data[k] = v

        try:
            r = requests.post(self.apiRoot+self.apiRoute,data=data)
            if r.status_code == 200:
                return r.content
            else:
                return '''{"result:{"success":false}}'''

        except Exception as e:
            return '''{"result:{"success":false,"msg":"%s"}}'''%str(e)


    def getOrderSimpleList(self,option={}):

        apiPath = 'api.findOrderListSimpleQuery'

        data = {'appKey':self.appKey,'apiPath':apiPath,'orderStatus':'','page':'1','pageSize':'20','createDateStart':'','createDateEnd':''}

        for (k,v) in  option.items():
            data[k] = v

        try:
            r = requests.post(self.apiRoot+self.apiRoute,data=data)
            if r.status_code == 200:
                return r.content
            else:
                return '''{"result:{"success":false}}'''

        except Exception as e:
            return '''{"result:{"success":false,"msg":"%s"}}'''%str(e)








