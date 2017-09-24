#coding:utf-8


from base import BaseHandler

from apps.alibaba.alibabaAPI import *
from apps.database.databaseCase import *
import json
import datetime
import re
import tornado.web


class PurchaseListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):


        user = self.current_user
        role = self.get_secure_cookie("role") if self.get_secure_cookie("role") else 'None'

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client

        db = client.woderp

        pageSize = 50

        status = self.get_argument('status','')
        wd = self.get_argument('wd','')


        try:
            page = int(self.get_argument('page',1))
        except:
            page = 1

        option = {}
        if status == '0':
            option['status'] = 'waitsellersend'
        elif status == '1':
            option['status'] = 'waitbuyerreceive'


        if wd != '':
            words = re.compile(wd)

            filerList = []
            filerList.append({'orderEntries.productName':words})
            filerList.append({'toFullName':words})
            filerList.append({'toMobile':words})
            filerList.append({'buyerAccount':words})
            filerList.append({'sellerCompanyName':words})
            filerList.append({'logistics.toContact':words})
            filerList.append({'logistics.logisticsBillNo':words})
            try:
                filerList.append({'id':int(wd)})
            except:
                pass

            option['$or'] = filerList


        totalCount = db.purchaseList.find(option).count()

        purchaseList = db.purchaseList.find(option).sort("gmtCreate",-1).limit(pageSize).skip((page-1)*pageSize)

        p = divmod(totalCount,pageSize)

        pageInfo = dict()

        totalPage = p[0]
        if p[1]>0:
            totalPage += 1

        pageInfo['totalPage'] = totalPage
        pageInfo['totalCount'] = totalCount
        pageInfo['pageSize'] = pageSize
        pageInfo['pageNo'] = page
        pageInfo['pageList'] = range(1,totalPage+1)

        filterData = dict()
        filterData['status'] = status
        filterData['wd'] = wd

        self.render('purchase-list.html',purchaseList = purchaseList,pageInfo = pageInfo,filterData=filterData,userInfo={'account':user,'role':role})

        #self.render('index.html')

    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error.\n" % status_code)


class CheckPurchaseHandler(BaseHandler):
    def get(self):

        data = dict()

        appKey = self.get_argument('appKey','1700674')
        orderStatus = self.get_argument('orderStatus','')
        pageNO = self.get_argument('pageNO','1')
        createStartTime = self.get_argument('createStartTime','')
        createEndTime = self.get_argument('createEndTime','')

        option = {'pageNO':pageNO}
        if orderStatus != '':
            option['orderStatus'] = orderStatus
        if createStartTime != '':
            option['createStartTime'] = createStartTime
        else:
            option['createStartTime'] = (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y-%m-%d %H:%M:%S')
        if createEndTime != '':
            option['createEndTime'] = createEndTime
        else:
            option['createEndTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


        data['total'] = 0
        data['addCount'] = 0
        data['success'] = False
        mongo = MongoCase()
        mongo.connect()
        client = mongo.client
        db = client.woderp

        app = db.appList.find_one({'platform':'1688','appKey':appKey})

        if app:
            api = ALIBABA(app)

            d = json.loads(api.getOrderList(option))

            if d.has_key('result') and d['result']['success']:

                ol = d['result']['toReturn']

                for od in ol:
                    item = od
                    item['createTime'] = datetime.datetime.now()
                    item['updateTime'] = None
                    #item['buyerAccount'] = 'tj18690821588'
                    item['dealCompleteTime'] = None
                    item['dealRemark'] = None


                    item['dealStatus'] = 0
                    item['stage'] = 0
                    item['oprationLog'] = []


                    if db.purchaseList.find({'id':int(item['id'])}).count()>0:
                        pass
                    else:
                        db.purchaseList.insert(item)
                        data['addCount'] += 1

                    data['total'] +=1

                data['success'] = True


        self.write(json.dumps(data, ensure_ascii=False))


class CheckPurchaseInfoHandler(BaseHandler):

    def get(self):
        data = dict()
        orderId = self.get_argument('orderId', '')
        if orderId != '':

            mongo = MongoCase()
            mongo.connect()
            client = mongo.client
            db = client.woderp

            od = db.purchaseList.find_one({"id": int(orderId)})
            if od:
                app = db.appList.find_one({'memberId':od['buyerMemberId']})
                api = ALIBABA(app)
                d = api.getOrderDetail(orderId)
                result = json.loads(d)

                if result.has_key('result') and result['result']['success']:

                    orderInfo = result['result']['toReturn'][0]

                    item = dict()

                    if orderInfo.has_key('logistics'):
                        item['logistics'] = orderInfo['logistics']

                    if orderInfo.has_key('sellerCompanyName'):
                        item['sellerCompanyName'] = orderInfo['sellerCompanyName']

                    if orderInfo.has_key('sellerPhone'):
                        item['sellerPhone'] = orderInfo['sellerPhone']

                    if orderInfo.has_key('sellerMobile'):
                        item['sellerMobile'] = orderInfo['sellerMobile']

                    item['orderEntries'] = orderInfo['orderEntries']

                    try:
                        d = datetime.datetime.strptime(orderInfo['gmtModified'][:14],'%Y%m%d%H%M%S')
                        item['gmtModified'] = d.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass

                    try:
                        d = datetime.datetime.strptime(orderInfo['gmtPayment'][:14],'%Y%m%d%H%M%S')
                        item['gmtPayment'] = d.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass


                    item['status'] = orderInfo['status']

                    item['updateTime'] = datetime.datetime.now()


                    db.purchaseList.update({"id": int(orderId)}, {'$set': item})

                    data['success'] = True

                else:
                    data['success'] = False
                    data['msg'] = 'Update ERROR'


        else:
            data['success'] = False
            data['msg'] = 'ERROR'

        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(json.dumps(data, ensure_ascii=False))


class CheckPurchaseLogistHandler(BaseHandler):

    def get(self):
        data = dict()
        ids = self.get_argument('ids', '')
        ids = ids.split(',')
        data['total'] = len(ids)
        data['successCount'] = 0
        data['errorCount'] = 0


        mongo = MongoCase()
        mongo.connect()
        client = mongo.client
        db = client.woderp

        for orderId in ids:

            od = db.purchaseList.find_one({"id": int(orderId)})

            app = db.appList.find_one({'memberId':od['buyerMemberId']})
            api = ALIBABA(app)

            d = api.getOrderDetail(orderId)
            result = json.loads(d)

            if result.has_key('result') and result['result']['success']:

                orderInfo = result['result']['toReturn'][0]

                item = dict()

                if orderInfo.has_key('logistics'):
                    item['logistics'] = orderInfo['logistics']

                if orderInfo.has_key('sellerCompanyName'):
                    item['sellerCompanyName'] = orderInfo['sellerCompanyName']

                if orderInfo.has_key('sellerPhone'):
                    item['sellerPhone'] = orderInfo['sellerPhone']

                if orderInfo.has_key('sellerMobile'):
                    item['sellerMobile'] = orderInfo['sellerMobile']

                item['orderEntries'] = orderInfo['orderEntries']

                try:
                    d = datetime.datetime.strptime(orderInfo['gmtModified'][:14],'%Y%m%d%H%M%S')
                    item['gmtModified'] = d.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass

                try:
                    d = datetime.datetime.strptime(orderInfo['gmtPayment'][:14],'%Y%m%d%H%M%S')
                    item['gmtPayment'] = d.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass


                item['status'] = orderInfo['status']

                item['updateTime'] = datetime.datetime.now()


                db.purchaseList.update({"id": int(orderId)}, {'$set': item})

                data['successCount'] += 1

            else:
                data['errorCount'] += 1


        self.write(json.dumps(data, ensure_ascii=False))



class getPurchaseInfoHandler(BaseHandler):

    def get(self):
        data = dict()
        orderId = self.get_argument('orderId', '')
        if orderId != '':

            mongo = MongoCase()
            mongo.connect()
            client = mongo.client
            db = client.woderp

            orderInfo = db.purchaseList.find_one({"id": int(orderId)})

            data['data'] = orderInfo
            data['data']['createTime'] = data['data']['createTime'].strftime('%Y-%m-%d %H:%M:%S')
            data['data']['updateTime'] = str(data['data']['updateTime'])
            data['data']['_id'] = str(data['data']['_id'])

            data['success'] = True

        else:
            data['success'] = False
            data['msg'] = 'ERROR'

        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(json.dumps(data, ensure_ascii=False))