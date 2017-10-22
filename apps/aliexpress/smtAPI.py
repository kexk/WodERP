#coding:utf-8


import requests
import json


class ALIEXPRESS:

    appKey = ''
    apiRoot = ''
    apiRoute = 'requestAPI.php'

    status = 0

    def __init__(self,app):
        self.appKey = app['apiInfo']['appKey']
        self.apiRoot = app['apiInfo']['apiRoot']

        d = self.getRemainingWindows()
        if d['success']:
            self.status = 1
        else:
            self.getToken()

    def getToken(self):

        try:
            r = requests.post(self.apiRoot+'getToken.php',data={'appKey':self.appKey})
            if r.status_code == 200:
                d = json.loads(r.content)

                if d.has_key('error_code'):
                    self.status = 0
                    return {'success':False,'errMsg':d['error_message']}
                else:
                    self.status = 1
                    return {'success':True}

            else:
                self.status = 0
                return {'success':False,'errMsg':['请求失败']}
        except:
            self.status = 0
            return {'success':False,'errMsg':['请求失败']}

    def getRemainingWindows(self):

        apiPath = 'api.getRemainingWindows'

        data = {'apiPath':apiPath,'appKey':self.appKey}

        try:
            r = requests.post(self.apiRoot+self.apiRoute,data=data)
            if r.status_code == 200:
                d = json.loads(r.content)
                if d.has_key('error_code'):
                    return {'success':False,'errMsg':d['error_message']}
                else:
                    return {'success':True,'data':d}
            else:
                return {'success':False,'errMsg':'请求失败'}
        except Exception as e:
            return {'success':False,'errMsg':'抛出异常','errorData':str(e)}

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

    def getOrderBaseInfo(self,orderId):

        apiPath = 'api.findOrderBaseInfo'


        data = {'orderId':orderId,'apiPath':apiPath,'appKey':self.appKey}

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


    #获取产品列表
    def getProductInfoList(self,option={}):

        #productStatusType:商品业务状态，目前提供4种，输入参数分别是：上架:onSelling ；下架:offline ；审核中:auditing ；审核不通过:editingRequired。

        apiPath = 'api.findProductInfoListQuery'

        data = {'appKey': self.appKey, 'apiPath': apiPath, 'productStatusType': 'onSelling', 'currentPage': '1', 'pageSize': '20',
                'subject': '', 'groupId': '', 'wsDisplay':'', 'offLineTime':'', 'productId':'', 'exceptedProductIds':''}

        for (k, v) in option.items():
            data[k] = v

        try:
            r = requests.post(self.apiRoot+self.apiRoute,data=data)
            if r.status_code == 200:
                return r.content
            else:
                return '''{"result:{"success":false}}'''

        except Exception as e:
            return '''{"result:{"success":false,"msg":"%s"}}'''%str(e)


    #获取产品详情
    def getProductById(self,productId):
        apiPath = 'api.findAeProductById'

        data = {'appKey': self.appKey, 'apiPath': apiPath, 'productId': productId}

        try:
            r = requests.post(self.apiRoot+self.apiRoute,data=data)
            if r.status_code == 200:
                return r.content
            else:
                return '''{"result:{"success":false}}'''

        except Exception as e:
            return '''{"result:{"success":false,"msg":"%s"}}'''%str(e)

    #查询产品状态
    def getProductStatusById(self,productId):
        apiPath = 'api.findAeProductStatusById'

        data = {'appKey': self.appKey, 'apiPath': apiPath, 'productId': productId}

        try:
            r = requests.post(self.apiRoot+self.apiRoute,data=data)
            if r.status_code == 200:
                return r.content
            else:
                return '''{"result:{"success":false}}'''

        except Exception as e:
            return '''{"result:{"success":false,"msg":"%s"}}'''%str(e)


    #查询运费模板列表
    def getFreightTemplateList(self):
        apiPath = 'api.listFreightTemplate'

        data = {'appKey': self.appKey, 'apiPath': apiPath}

        try:
            r = requests.post(self.apiRoot+self.apiRoute,data=data)
            if r.status_code == 200:
                return r.content
            else:
                return '''{"result:{"success":false}}'''

        except Exception as e:
            return '''{"result:{"success":false,"msg":"%s"}}'''%str(e)

    # 查询运费模板列表
    def getFreightTemplateDetail(self,templateId):
        apiPath = 'api.getFreightSettingByTemplateQuery'

        data = {'appKey': self.appKey, 'apiPath': apiPath,'templateId':templateId}

        try:
            r = requests.post(self.apiRoot + self.apiRoute, data=data)
            if r.status_code == 200:
                return r.content
            else:
                return '''{"result:{"success":false}}'''

        except Exception as e:
            return '''{"result:{"success":false,"msg":"%s"}}''' % str(e)


    # 运费计算
    def calculateFreight(self,option={}):
        apiPath = 'api.calculateFreight'

        data = {'appKey': self.appKey, 'apiPath': apiPath,'freightTemplateId':'',
                'country':'','weight':'','length':'','width':'','height':'',
                'productPrice':'','count':'','customPackWeight':'',
                'packBaseUnit':'','packAddUnit':'','packAddWeight':''}

        for (k, v) in option.items():
            data[k] = v

        try:
            r = requests.post(self.apiRoot + self.apiRoute, data=data)
            if r.status_code == 200:
                return r.content
            else:
                return '''{"result:{"success":false}}'''

        except Exception as e:
            return '''{"result:{"success":false,"msg":"%s"}}''' % str(e)

