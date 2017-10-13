#coding:utf-8


from base import BaseHandler

from apps.aliexpress.smtAPI import *
from apps.database.databaseCase import *
import json
import datetime
import random

import re
import tornado.web
import tornado.httpclient
import tornado.gen
from tornado.httpclient import HTTPRequest


class SMTOrderListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):

        AUTHOR_MOUDLE = 'ViewSMTOrder'

        user = self.current_user
        role = self.get_secure_cookie("role") if self.get_secure_cookie("role") else 'None'

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client

        db = client.woderp

        account = db.user.find_one({'account':user})

        authority = self.getAuthority(account,AUTHOR_MOUDLE)

        if authority['Allow']:

            pageSize = 100

            status = self.get_argument('status','')
            store = self.get_argument('store','')
            wd = self.get_argument('wd','')
            platform = self.get_argument('platform','aliexpress')

            try:
                page = int(self.get_argument('page',1))
            except:
                page = 1

            #totalCount = db.orderList.find({"order_state":"WAIT_SELLER_STOCK_OUT"}).count()
            option = {'platform':platform}

            matchOption = dict()

            if authority['role'] == 'Supper':
                appList = db.appList.find({'platform': 'aliexpress'})
            else:
                appList = db.appList.find({'platform': 'aliexpress','storeId':{'$in':authority['authority']['smtStore']}})


            if status != '':
                option['orderStatus'] = status
                matchOption['orderStatus'] = status

            if store != '':
                option['storeInfo.storeId'] = store
                matchOption['storeInfo.storeId'] = store
            elif authority['role'] != 'Supper' :
                option['storeInfo.storeId'] = {'$in':authority['authority']['smtStore']}
                matchOption['storeInfo.storeId'] = {'$in':authority['authority']['smtStore']}

            statusList = db.orderList.aggregate([{ '$match' : matchOption },{'$group': {'_id': "$orderStatus", 'orderCount': {'$sum': 1}}}])

            sL = []
            for s in statusList:
                if s['_id']:
                    stxt = ''
                    if s['_id'] == 'PLACE_ORDER_SUCCESS':
                        stxt += '未付款'
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
                    sL.append({'status': s['_id'], 'orderCount': s['orderCount'], 'statusTxt': stxt})


            if wd != '':
                words = re.compile(wd)

                filerList = []
                filerList.append({'productList.productName':words})
                filerList.append({'productList.skuCode':words})
                filerList.append({'buyerLoginId':words})
                filerList.append({'buyerSignerFullname':words})
                filerList.append({'receiptAddress.contactPerson':words})
                filerList.append({'receiptAddress.mobileNo':words})
                filerList.append({'logisticInfoList.logisticsNo':words})
                filerList.append({'orderId':words})
                filerList.append({'productList.productId':words})

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
            filterData['store'] = store
            filterData['wd'] = wd
            filterData['statusList'] = sL
            filterData['appList'] = appList

            self.render('smt/order-list.html',orderList = orderList,pageInfo = pageInfo,filterData=filterData,userInfo={'account':user,'role':role})

            #self.render('index.html')

        else:
            #self.write("No Permission")
            self.render('error/message.html', msg={'Msg': 'No Permission', 'Code': 400,'Title':'无权限！','Link':'/'})



class SMTCheckOrderHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):

        #result = o.getOrderList(order_state='WAIT_GOODS_RECEIVE_CONFIRM')

        storeId = self.get_argument('storeId','')
        status = self.get_argument('status','')
        url = "http://127.0.0.1:5000/smt/api/checkOrder?storeId=%s&status=%s" % (storeId, status)
        request = HTTPRequest(url=url,method="GET",follow_redirects=False,request_timeout=3000)
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, request)
        result = json.loads(response.body)
        self.write(result)
        self.finish()


class SMTRefreshOrderStatusHandler(BaseHandler):
    def get(self):
        data = dict()
        items = self.get_argument('items', '')
        ol = json.loads(items)

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client
        db = client.woderp

        for (k,v) in  ol.items():
            app = db.appList.find_one({'storeId': k})
            if app != None:
                api = ALIEXPRESS(app)
                ids = v.strip(',').split(',')
                for id in ids:
                    c = api.getOrderBaseInfo(id)
                    d = json.loads(c)
                    if d != {}:
                        newData = d
                        newData['gmtModified'] = datetime.datetime.strptime(newData['gmtModified'], '%Y-%m-%d %H:%M:%S')
                        newData['gmtCreate'] = datetime.datetime.strptime(newData['gmtCreate'], '%Y-%m-%d %H:%M:%S')

                        if newData['orderStatus'] == 'FINISH' or newData['orderStatus'] == 'WAIT_BUYER_ACCEPT_GOODS' or newData['orderStatus'] == 'FUND_PROCESSING':
                            newData['timeoutLeftTime'] = None
                            newData['leftSendGoodMin'] = None
                            newData['leftSendGoodDay'] = None
                            newData['leftSendGoodHour'] = None

                        db.orderList.update({'orderId':id},{'$set':newData})

        data['success'] = True

        self.write(json.dumps(data, ensure_ascii=False))
