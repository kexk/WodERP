#coding:utf-8


from base import BaseHandler

from apps.aliexpress.smtAPI import *
from apps.database.databaseCase import *
import json
import datetime

import re
import tornado.web


class SMTOrderListHandler(BaseHandler):
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

        #totalCount = db.orderList.find({"order_state":"WAIT_SELLER_STOCK_OUT"}).count()
        option = {'platform':'aliexpress'}
        if status == '0':
            option['orderStatus'] = 'PLACE_ORDER_SUCCESS'
        elif status == '1':
            option['orderStatus'] = 'RISK_CONTROL'
        elif status == '2':
            option['orderStatus'] = 'IN_CANCEL'
        elif status == '3':
            option['orderStatus'] = 'WAIT_SELLER_SEND_GOODS'
        elif status == '4':
            option['orderStatus'] = 'SELLER_PART_SEND_GOODS'
        elif status == '5':
            option['orderStatus'] = 'WAIT_BUYER_ACCEPT_GOODS'
        elif status == '6':
            option['orderStatus'] = 'IN_ISSUE'
        elif status == '7':
            option['orderStatus'] = 'IN_FROZEN'
        elif status == '8':
            option['orderStatus'] = 'FUND_PROCESSING'
        elif status == '9':
            option['orderStatus'] = 'WAIT_SELLER_EXAMINE_MONEY'
        elif status == '10':
            option['orderStatus'] = 'FINISH'


        if wd != '':
            words = re.compile(wd)

            filerList = []
            filerList.append({'productList.productName':words})
            filerList.append({'buyerLoginId':words})
            filerList.append({'buyerSignerFullname':words})
            filerList.append({'receiptAddress.contactPerson':words})
            filerList.append({'receiptAddress.mobileNo':words})
            filerList.append({'logisticInfoList.logisticsNo':words})

            try:
                filerList.append({'orderId':int(wd)})
            except:
                pass

            option['$or'] = filerList



        totalCount = db.orderList.find(option).count()

        orderList = db.orderList.find(option).sort("gmtPayTime",-1).limit(pageSize).skip((page-1)*pageSize)

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

        self.render('smt/order-list.html',orderList = orderList,pageInfo = pageInfo,filterData=filterData,userInfo={'account':user,'role':role})

        #self.render('index.html')

    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error.\n" % status_code)

class SMTCheckOrderHandler(BaseHandler):
    def get(self):

        #result = o.getOrderList(order_state='WAIT_GOODS_RECEIVE_CONFIRM')

        appKey = self.get_argument('appKey')

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client
        db = client.woderp

        app = db.storeList.find_one({'apiInfo.appKey':appKey})

        if app != None:

            api = ALIEXPRESS(app)

            #option = {'orderStatus':'WAIT_SELLER_SEND_GOODS'}
            option = {}

            c = api.getOrderList(option)

            result = json.loads(c)

            ol = result['orderList']
            total = result['totalItem']
            addCount = 0
            updateCount = 0
            for od in ol:
                item = od
                item['createTime'] = datetime.datetime.now()
                item['updateTime'] = None
                item['storeId'] = app['storeId']
                item['platform'] = 'aliexpress'

                item['dealStatus'] = 'WAIT_SYSTEM_CHECK'
                item['oprationLog'] = []
                item['weight'] = None
                item['totalCost'] = None
                item['totalProfit'] = None
                item['isLock'] = 0
                item['type'] = 0
                item['isShelve'] = 0
                item['isShelve'] = 0
                item['errorMsg'] = None
                item['isMakeup'] = 0
                item['reSendReason'] = 0
                item['isMergeOrder'] = 0
                item['isSplitOrder'] = 0
                item['hasMessage'] = 0
                item['isDelivery'] = 0
                item['checkName'] = 0
                item['orderMemo'] = []
                item['labels'] = []
                item['pickStatus'] = 0


                for sku in item['productList']:
                    sku['skuId'] = None
                    sku['skuAttr'] = None
                    sku['purchaseNo'] = None
                    sku['weight'] = None
                    sku['pickStatus'] = 0


                if db.orderList.find({'orderId':int(item['orderId'])}).count()>0:
                    updateCount += 1
                else:
                    db.orderList.insert(item)
                    addCount += 1


            respon = {'success': True,"data":{"total":total,"addCount":addCount,'updateCount':updateCount}}

            self.write(json.dumps(respon,ensure_ascii=False))
        else:
            self.write(json.dumps({'success':False},ensure_ascii=False))