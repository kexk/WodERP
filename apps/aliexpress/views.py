#coding:utf-8


from base import BaseHandler

from apps.aliexpress.smtAPI import *
from apps.database.databaseCase import *
import json
import datetime
import random

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

        pageSize = 100

        status = self.get_argument('status','WAIT_SELLER_SEND_GOODS')
        wd = self.get_argument('wd','')


        try:
            page = int(self.get_argument('page',1))
        except:
            page = 1

        #totalCount = db.orderList.find({"order_state":"WAIT_SELLER_STOCK_OUT"}).count()
        option = {'platform':'aliexpress'}

        statusList = db.orderList.aggregate([{'$group' : {'_id' : "$orderStatus", 'orderCount': {'$sum' : 1}}}])

        sL = []
        for s in statusList:
            if s['_id']:
                stxt = ''
                if s['_id'] == 'PLACE_ORDER_SUCCESS':
                    stxt += '待付款'
                elif s['_id'] == 'RISK_CONTROL':
                    stxt += '风控中'
                elif s['_id'] == 'IN_CANCEL':
                    stxt += '已取消'
                elif s['_id'] == 'WAIT_SELLER_SEND_GOODS':
                    stxt += '待发货'
                elif s['_id'] == 'SELLER_PART_SEND_GOODS':
                    stxt += '部分发货'
                elif s['_id'] == 'WAIT_BUYER_ACCEPT_GOODS':
                    stxt += '待收货'
                elif s['_id'] == 'IN_ISSUE':
                    stxt += '纠纷中'
                elif s['_id'] == 'IN_FROZEN':
                    stxt += '冻结中'
                elif s['_id'] == 'FUND_PROCESSING':
                    stxt += '待放款'
                elif s['_id'] == 'WAIT_SELLER_EXAMINE_MONEY':
                    stxt += '待确认金额'
                elif s['_id'] == 'FINISH':
                    stxt += '已结束'
                sL.append({'status':s['_id'],'orderCount':s['orderCount'],'statusTxt':stxt})


        option['orderStatus'] = status


        if wd != '':
            words = re.compile(wd)

            filerList = []
            filerList.append({'productList.productName':words})
            filerList.append({'buyerLoginId':words})
            filerList.append({'buyerSignerFullname':words})
            filerList.append({'receiptAddress.contactPerson':words})
            filerList.append({'receiptAddress.mobileNo':words})
            filerList.append({'logisticInfoList.logisticsNo':words})
            filerList.append({'productList.productId':int(wd)})

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
        filterData['statusList'] = sL

        self.render('smt/order-list.html',orderList = orderList,pageInfo = pageInfo,filterData=filterData,userInfo={'account':user,'role':role})

        #self.render('index.html')

    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error.\n" % status_code)


class SMTCheckOrderHandler(BaseHandler):
    def get(self):

        #result = o.getOrderList(order_state='WAIT_GOODS_RECEIVE_CONFIRM')

        storeId = self.get_argument('storeId','')

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client
        db = client.woderp

        appList = db.appList.find({'platform':'aliexpress'})

        if storeId == '':
            #appKey = aList[random.randint(0,len(aList)-1)]
            app = appList[random.randint(0,len(appList)-1)]
        else:
            app = db.appList.find_one({'storeId': storeId})

        if app != None:

            api = ALIEXPRESS(app)

            option = dict()
            #option = {'orderStatus':'WAIT_SELLER_SEND_GOODS'}
            option['pageSize'] = '50'
            option['orderStatus'] = 'WAIT_SELLER_SEND_GOODS'

            c = api.getOrderList(option)

            result = json.loads(c)

            ol = result['orderList']
            total = result['totalItem']
            addCount = 0
            updateCount = 0
            for od in ol:
                item = od
                item['createTime'] = datetime.datetime.now()
                item['updateTime'] = datetime.datetime.now()
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


                order = db.orderList.find_one({'orderId':int(item['orderId'])})
                if order:
                    newData = dict()
                    newData['productList'] = item['productList']
                    newData['orderStatus'] = item['orderStatus']
                    newData['frozenStatus'] = item['frozenStatus']
                    newData['issueStatus'] = item['issueStatus']
                    newData['fundStatus'] = item['fundStatus']
                    if item.has_key('timeoutLeftTime'):
                        newData['timeoutLeftTime'] = item['timeoutLeftTime']
                    if item.has_key('leftSendGoodMin'):
                        newData['leftSendGoodMin'] = item['leftSendGoodMin']
                    if item.has_key('leftSendGoodHour'):
                        newData['leftSendGoodHour'] = item['leftSendGoodHour']
                    if item.has_key('leftSendGoodDay'):
                        newData['leftSendGoodDay'] = item['leftSendGoodDay']

                    if item.has_key('memo'):
                        newData['memo'] = item['memo']

                    if not order.has_key('gmtPayTime') and item.has_key('gmtPayTime'):
                        newData['gmtPayTime'] = item['gmtPayTime']

                    db.orderList.update({'orderId':int(item['orderId'])},{'$set':newData})

                    updateCount += 1
                else:
                    db.orderList.insert(item)
                    addCount += 1


            respon = {'success': True,"data":{"total":total,"addCount":addCount,'updateCount':updateCount}}

            self.write(json.dumps(respon,ensure_ascii=False))
        else:
            self.write(json.dumps({'success':False},ensure_ascii=False))