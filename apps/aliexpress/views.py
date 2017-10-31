#coding:utf-8


from base import BaseHandler

from apps.database.databaseCase import *
import json
import pytz

import datetime

import re
import tornado.web
import tornado.httpclient
import tornado.gen
from tornado.httpclient import HTTPRequest
import urllib

apiServer = 'http://127.0.0.1:5000'


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

        tz = pytz.timezone('America/Los_Angeles')
        LosAngelesTime = datetime.datetime.now(tz)

        account = db.user.find_one({'account':user})

        authority = self.getAuthority(account,AUTHOR_MOUDLE)

        if authority['Allow']:

            status = self.get_argument('status','WAIT_SELLER_SEND_GOODS')
            store = self.get_argument('store','')
            wd = self.get_argument('wd','')
            sort = self.get_argument('sort', 'payTime')
            sortType = self.get_argument('sortType', '-1')
            create = self.get_argument('create', '30')
            startTime = self.get_argument('startTime', '')
            endTime = self.get_argument('endTime', '')
            platform = self.get_argument('platform','aliexpress')

            try:
                page = int(self.get_argument('page',1))
            except:
                page = 1

            try:
                pageSize = int(self.get_argument('pageSize',50))
            except:
                pageSize = 50

            #totalCount = db.orderList.find({"order_state":"WAIT_SELLER_STOCK_OUT"}).count()
            option = {'platform':platform}

            #匹配
            matchOption = dict()

            #筛选合并发货订单
            filterOption = dict()
            filterOption['count'] = {'$gt': 1}
            filterOption['orderStatus'] = "WAIT_SELLER_SEND_GOODS"


            if authority['role'] == 'Supper':
                appList = db.appList.find({'platform': 'aliexpress'})
            else:
                appList = db.appList.find({'platform': 'aliexpress','storeId':{'$in':authority['authority']['smtStore']}})


            if status != '':
                option['orderStatus'] = status
                #matchOption['orderStatus'] = status

            if store != '':
                option['storeInfo.storeId'] = store
                matchOption['storeInfo.storeId'] = store
                filterOption['storeId'] = store
            elif authority['role'] != 'Supper' :
                option['storeInfo.storeId'] = {'$in':authority['authority']['smtStore']}
                matchOption['storeInfo.storeId'] = {'$in':authority['authority']['smtStore']}
                filterOption['storeId'] = {'$in': authority['authority']['smtStore']}


            tStart = ''
            tEnd = ''

            if startTime != '' and endTime != '':
                try:
                    d0 = datetime.datetime.strptime(startTime,'%Y-%m-%d')
                    d1 = datetime.datetime.strptime(endTime,'%Y-%m-%d')

                    if d0 == d1:
                        tStart = d0.strftime('%Y-%m-%d')
                        d1 = d1+datetime.timedelta(days=1)
                        tEnd = d1.strftime('%Y-%m-%d')
                        option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                          {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                        matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                               {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    elif d0 > d1:
                        tStart = d1.strftime('%Y-%m-%d')
                        tEnd = d0.strftime('%Y-%m-%d')
                        option['$and'] = [{'gmtCreate': {'$lt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                          {'gmtCreate': {'$gt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                        matchOption['$and'] = [{'gmtCreate': {'$lt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                               {'gmtCreate': {'$gt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    else:
                        tStart = d0.strftime('%Y-%m-%d')
                        tEnd = d1.strftime('%Y-%m-%d')
                        option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                          {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                        matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                               {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]

                except:

                    d1 = datetime.datetime.now().date()
                    d0 = datetime.datetime.now().date()+ datetime.timedelta(days=-29)
                    option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]

                    tStart = d0.strftime('%Y-%m-%d')
                    tEnd = d1.strftime('%Y-%m-%d')

            else:

                if create == '30':
                    d1 = datetime.datetime.now().date() + datetime.timedelta(days=1)
                    d0 = datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
                    option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                           {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                elif create == '7':
                    d1 = datetime.datetime.now().date() + datetime.timedelta(days=1)
                    d0 = datetime.datetime.now().date() + datetime.timedelta(days=-6)
                    option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                           {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                elif create == '3':
                    d1 = datetime.datetime.now().date() + datetime.timedelta(days=1)
                    d0 = datetime.datetime.now().date() + datetime.timedelta(days=-2)
                    option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                           {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                elif create == '1':
                    d1 = datetime.datetime.now().date()
                    d0 = datetime.datetime.now().date() + datetime.timedelta(days=-1)
                    option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                           {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                elif create == '0':
                    d1 = datetime.datetime.now().date() + datetime.timedelta(days=1)
                    d0 = datetime.datetime.now().date()
                    option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                           {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]


            statusList = db.orderList.aggregate([{ '$match' : matchOption },{'$group': {'_id': "$orderStatus", 'orderCount': {'$sum': 1}}}])


            sortTxt = ''

            if sort == 'gmtCreate':
                sortTxt += 'gmtCreate'
            if sort == 'timeoutLeftTime':
                sortTxt += 'timeoutLeftTime'
            elif sort == 'orderAmount':
                sortTxt += 'orderAmount'
            elif sort == 'orderAmount':
                sortTxt += 'orderAmount'
            elif sort == 'orderId':
                sortTxt += 'orderId'
            elif sort == 'storeId':
                sortTxt += 'soteInfo.storeId'
            else:
                sortTxt += 'gmtPayTime'


            sortT = -1

            try:
                t = int(sortType)
                if t >= 1:
                    sortT = 1
                else:
                    sortT = -1
            except:
                sortT = -1


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

            mergeOrder = db.orderList.aggregate(
                [{'$group': {
                    '_id': {'contactPerson': "$receiptAddress.contactPerson",
                            'country': "$receiptAddress.country",
                            'orderStatus': "$orderStatus",
                            'storeId': "$storeInfo.storeId"
                            },
                    'uniqueIds': {'$addToSet': "$_id"},
                    'count': {'$sum': 1},
                    'orderStatus': {'$first': "$orderStatus"},
                    'storeId': {'$first': "$storeInfo.storeId"},
                }},
                    {'$match': filterOption}
                ])

            MergeCount = 0
            for item in mergeOrder:
                if item['_id'].has_key('contactPerson'):
                    MergeCount += 1

            totalCount = db.orderList.find(option).count()

            orderList = db.orderList.find(option).sort(sortTxt,sortT).limit(pageSize).skip((page-1)*pageSize)

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
            filterData['sort'] = sort
            filterData['startTime'] = tStart
            filterData['endTime'] = tEnd
            filterData['create'] = create
            filterData['sortType'] = sortType

            self.render('smt/order-list.html',orderList = orderList,pageInfo = pageInfo,MergeCount=MergeCount,LosAngelesTime=LosAngelesTime,filterData=filterData,userInfo={'account':user,'role':role})

            #self.render('index.html')

        else:
            #self.write("No Permission")
            self.render('error/message.html', msg={'Msg': 'No Permission', 'Code': 400,'Title':'无权限！','Link':'/'})


class SMTOrderListHandlerV2(BaseHandler):
    @tornado.web.authenticated
    def get(self):

        AUTHOR_MOUDLE = 'ViewSMTOrder'

        user = self.current_user
        role = self.get_secure_cookie("role") if self.get_secure_cookie("role") else 'None'

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client

        db = client.woderp

        tz = pytz.timezone('America/Los_Angeles')
        LosAngelesTime = datetime.datetime.now(tz)

        account = db.user.find_one({'account':user})

        authority = self.getAuthority(account,AUTHOR_MOUDLE)

        if authority['Allow']:

            status = self.get_argument('status','WAIT_SELLER_SEND_GOODS')
            store = self.get_argument('store','')
            wd = self.get_argument('wd','')
            sort = self.get_argument('sort', 'payTime')
            sortType = self.get_argument('sortType', '-1')
            create = self.get_argument('create', '30')
            startTime = self.get_argument('startTime', '')
            endTime = self.get_argument('endTime', '')
            platform = self.get_argument('platform','aliexpress')

            try:
                page = int(self.get_argument('page',1))
            except:
                page = 1

            try:
                pageSize = int(self.get_argument('pageSize',50))
            except:
                pageSize = 50

            #totalCount = db.orderList.find({"order_state":"WAIT_SELLER_STOCK_OUT"}).count()
            option = {'platform':platform}

            #匹配
            matchOption = dict()

            #筛选合并发货订单
            filterOption = dict()
            filterOption['count'] = {'$gt': 1}
            filterOption['orderStatus'] = "WAIT_SELLER_SEND_GOODS"


            if authority['role'] == 'Supper':
                appList = db.appList.find({'platform': 'aliexpress'})
            else:
                appList = db.appList.find({'platform': 'aliexpress','storeId':{'$in':authority['authority']['smtStore']}})


            if status != '':
                option['orderStatus'] = status
                #matchOption['orderStatus'] = status

            if store != '':
                option['storeInfo.storeId'] = store
                matchOption['storeInfo.storeId'] = store
                filterOption['storeId'] = store
            elif authority['role'] != 'Supper' :
                option['storeInfo.storeId'] = {'$in':authority['authority']['smtStore']}
                matchOption['storeInfo.storeId'] = {'$in':authority['authority']['smtStore']}
                filterOption['storeId'] = {'$in': authority['authority']['smtStore']}


            tStart = ''
            tEnd = ''

            if startTime != '' and endTime != '':
                try:
                    d0 = datetime.datetime.strptime(startTime,'%Y-%m-%d')
                    d1 = datetime.datetime.strptime(endTime,'%Y-%m-%d')

                    if d0 == d1:
                        tStart = d0.strftime('%Y-%m-%d')
                        d1 = d1+datetime.timedelta(days=1)
                        tEnd = d1.strftime('%Y-%m-%d')
                        option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                          {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                        matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                               {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    elif d0 > d1:
                        tStart = d1.strftime('%Y-%m-%d')
                        tEnd = d0.strftime('%Y-%m-%d')
                        option['$and'] = [{'gmtCreate': {'$lt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                          {'gmtCreate': {'$gt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                        matchOption['$and'] = [{'gmtCreate': {'$lt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                               {'gmtCreate': {'$gt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    else:
                        tStart = d0.strftime('%Y-%m-%d')
                        tEnd = d1.strftime('%Y-%m-%d')
                        option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                          {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                        matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                               {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]

                except:

                    d1 = datetime.datetime.now().date()
                    d0 = datetime.datetime.now().date()+ datetime.timedelta(days=-29)
                    option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]

                    tStart = d0.strftime('%Y-%m-%d')
                    tEnd = d1.strftime('%Y-%m-%d')

            else:

                if create == '30':
                    d1 = datetime.datetime.now().date() + datetime.timedelta(days=1)
                    d0 = datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
                    option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                           {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                elif create == '7':
                    d1 = datetime.datetime.now().date() + datetime.timedelta(days=1)
                    d0 = datetime.datetime.now().date() + datetime.timedelta(days=-6)
                    option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                           {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                elif create == '3':
                    d1 = datetime.datetime.now().date() + datetime.timedelta(days=1)
                    d0 = datetime.datetime.now().date() + datetime.timedelta(days=-2)
                    option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                           {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                elif create == '1':
                    d1 = datetime.datetime.now().date()
                    d0 = datetime.datetime.now().date() + datetime.timedelta(days=-1)
                    option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                           {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                elif create == '0':
                    d1 = datetime.datetime.now().date() + datetime.timedelta(days=1)
                    d0 = datetime.datetime.now().date()
                    option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                      {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                    matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                           {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]


            statusList = db.smtOrderList.aggregate([{ '$match' : matchOption },{'$group': {'_id': "$orderStatus", 'orderCount': {'$sum': 1}}}])


            sortTxt = ''

            if sort == 'gmtCreate':
                sortTxt += 'gmtCreate'
            if sort == 'timeoutLeftTime':
                sortTxt += 'timeoutLeftTime'
            elif sort == 'orderAmount':
                sortTxt += 'orderAmount'
            elif sort == 'orderAmount':
                sortTxt += 'orderAmount'
            elif sort == 'orderId':
                sortTxt += 'orderId'
            elif sort == 'storeId':
                sortTxt += 'soteInfo.storeId'
            else:
                sortTxt += 'gmtPayTime'


            sortT = -1

            try:
                t = int(sortType)
                if t >= 1:
                    sortT = 1
                else:
                    sortT = -1
            except:
                sortT = -1


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

            mergeOrder = db.smtOrderList.aggregate(
                [{'$group': {
                    '_id': {'contactPerson': "$receiptAddress.contactPerson",
                            'country': "$receiptAddress.country",
                            'orderStatus': "$orderStatus",
                            'storeId': "$storeInfo.storeId"
                            },
                    'uniqueIds': {'$addToSet': "$_id"},
                    'count': {'$sum': 1},
                    'orderStatus': {'$first': "$orderStatus"},
                    'storeId': {'$first': "$storeInfo.storeId"},
                }},
                    {'$match': filterOption}
                ])

            MergeCount = 0
            for item in mergeOrder:
                if item['_id'].has_key('contactPerson'):
                    MergeCount += 1

            totalCount = db.smtOrderList.find(option).count()

            orderList = db.smtOrderList.find(option).sort(sortTxt,sortT).limit(pageSize).skip((page-1)*pageSize)

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
            filterData['sort'] = sort
            filterData['startTime'] = tStart
            filterData['endTime'] = tEnd
            filterData['create'] = create
            filterData['sortType'] = sortType

            self.render('smt/order-list.html',orderList = orderList,pageInfo = pageInfo,MergeCount=MergeCount,LosAngelesTime=LosAngelesTime,filterData=filterData,userInfo={'account':user,'role':role})

            #self.render('index.html')

        else:
            #self.write("No Permission")
            self.render('error/message.html', msg={'Msg': 'No Permission', 'Code': 400,'Title':'无权限！','Link':'/'})


class SMTOrderMergeHandler(BaseHandler):
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

            status = self.get_argument('status','')
            store = self.get_argument('store','')
            platform = self.get_argument('platform','aliexpress')

            option = {'platform':platform}

            matchOption = dict()

            if authority['role'] == 'Supper':
                appList = db.appList.find({'platform': 'aliexpress'})
            else:
                appList = db.appList.find({'platform': 'aliexpress','storeId':{'$in':authority['authority']['smtStore']}})

            if status != '':
                option['orderStatus'] = status
                #matchOption['orderStatus'] = status

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


            mergeOrder = db.orderList.aggregate(
                [{'$group': {
                    '_id': {'contactPerson': "$receiptAddress.contactPerson",
                            'country': "$receiptAddress.country",
                            'orderStatus': "$orderStatus",
                            'storeId': "$storeInfo.storeId"
                            },
                    'uniqueIds': {'$addToSet': "$_id"},
                    'count': {'$sum': 1},
                    'orderStatus': {'$max': "$orderStatus"}
                }},
                    {'$match': {
                        'count': {'$gt': 1},
                        "orderStatus": "WAIT_SELLER_SEND_GOODS"
                    }
                    }
                ])

            orderList = []

            for item in mergeOrder:
                if item['_id'].has_key('contactPerson'):
                    orderItem = []
                    for id in item['uniqueIds']:
                        option['_id'] = id
                        orderItem.append(db.orderList.find_one(option))
                    orderList.append({'orderItems':orderItem,'_id':item["_id"]})

            filterData = dict()
            filterData['status'] = status
            filterData['store'] = store
            filterData['statusList'] = sL
            filterData['appList'] = appList

            self.render('smt/merge-order-list.html',orderList = orderList,filterData=filterData,userInfo={'account':user,'role':role})

            #self.render('index.html')

        else:
            #self.write("No Permission")
            self.render('error/message.html', msg={'Msg': 'No Permission', 'Code': 400,'Title':'无权限！','Link':'/'})


class SMTOrderManagerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):

        AUTHOR_MOUDLE = 'ViewSMTOrderManager'

        user = self.current_user
        role = self.get_secure_cookie("role") if self.get_secure_cookie("role") else 'None'

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client

        db = client.woderp

        account = db.user.find_one({'account':user})
        authority = self.getAuthority(account,AUTHOR_MOUDLE)

        if authority['Allow']:

            params = dict()
            params['createDateStart'] = (datetime.datetime.now() +datetime.timedelta(days=-10)).strftime('%Y-%m-%d 00:00:00')
            params['createDateEnd'] = datetime.datetime.now().strftime('%Y-%m-%d %H:00:00')

            if authority['role'] == 'Supper':
                appList = db.appList.find({'platform': 'aliexpress'})
            else:
                appList = db.appList.find({'platform': 'aliexpress','storeId':{'$in':authority['authority']['smtStore']}})

            self.render('smt/order-manager.html',appList = appList,params=params,userInfo={'account':user,'role':role})

        else:
            self.render('error/message.html', msg={'Msg': 'No Permission', 'Code': 400,'Title':'无权限！','Link':'/'})


    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        data = dict()

        data['storeId'] = self.get_argument('storeId','')
        data['status'] = self.get_argument('orderStatus','')
        data['createDateStart'] = self.get_argument('createDateStart','')
        data['createDateEnd'] = self.get_argument('createDateEnd','')

        url = apiServer+"/smt/api/checkOrder?" +urllib.urlencode(data)
        request = HTTPRequest(url=url,method="GET",follow_redirects=False,request_timeout=30000)

        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, request)
        try:
            result = json.loads(response.body)
        except Exception as e:
            result = {'success':False,'error':[{"storeId":data['storeId'],"options":data,"errMsg":str(e)}]}
        self.write(result)
        self.finish()



class SMTProductListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):

        AUTHOR_MOUDLE = 'ViewSMTProduct'

        user = self.current_user
        role = self.get_secure_cookie("role") if self.get_secure_cookie("role") else 'None'

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client

        db = client.woderp

        account = db.user.find_one({'account':user})

        authority = self.getAuthority(account,AUTHOR_MOUDLE)

        sortList = ['gmtModified','gmtCreate','wsOfflineDate','stock','price']

        if authority['Allow']:

            pageSize = 200

            status = self.get_argument('status','onSelling')
            store = self.get_argument('store','')
            wd = self.get_argument('wd','')
            sort = self.get_argument('sort','gmtModified')
            create = self.get_argument('create','')
            platform = self.get_argument('platform','aliexpress')

            sortTxt = ''

            if sort not in sortList:
                sortTxt += 'gmtModified'
            else:
                if sort == 'stock':
                    sortTxt += 'aeopAeProductSKUs.ipmSkuStock'
                elif sort == 'price':
                    sortTxt += 'aeopAeProductSKUs.skuPrice'
                else:
                    sortTxt += sort

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
                option['productStatusType'] = status
                #matchOption['productStatusType'] = status

            if store != '':
                option['storeInfo.storeId'] = store
                matchOption['storeInfo.storeId'] = store
            elif authority['role'] != 'Supper' :
                option['storeInfo.storeId'] = {'$in':authority['authority']['smtStore']}
                matchOption['storeInfo.storeId'] = {'$in':authority['authority']['smtStore']}


            if create == '30':
                d1 = datetime.datetime.now().date()+ datetime.timedelta(days=1)
                d0 = datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
                option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                  {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                  {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
            elif create == '7':
                d1 = datetime.datetime.now().date() + datetime.timedelta(days=1)
                d0 = datetime.datetime.now().date()+ datetime.timedelta(days=-6)
                option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                  {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                  {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
            elif create == '3':
                d1 = datetime.datetime.now().date() + datetime.timedelta(days=1)
                d0 = datetime.datetime.now().date() + datetime.timedelta(days=-2)
                option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                  {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                  {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
            elif create == '1':
                d1 = datetime.datetime.now().date()
                d0 = datetime.datetime.now().date() + datetime.timedelta(days=-1)
                option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                  {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
                matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                  {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]
            elif create == '0':
                d1 = datetime.datetime.now().date() + datetime.timedelta(days=1)
                d0 = datetime.datetime.now().date()
                option['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year,d0.month,d0.day)}}, {'gmtCreate': {'$lt': datetime.datetime(d1.year,d1.month,d1.day)}}]
                matchOption['$and'] = [{'gmtCreate': {'$gt': datetime.datetime(d0.year, d0.month, d0.day)}},
                                  {'gmtCreate': {'$lt': datetime.datetime(d1.year, d1.month, d1.day)}}]

            statusList = db.productList.aggregate([{ '$match' : matchOption },{'$group': {'_id': "$productStatusType", 'Count': {'$sum': 1}}}])

            sL = []
            for s in statusList:
                if s['_id']:
                    stxt = ''
                    if s['_id'] == 'onSelling':
                        stxt += '上架'
                    elif s['_id'] == 'offline':
                        stxt += '下架'
                    elif s['_id'] == 'auditing':
                        stxt += '审核中'
                    elif s['_id'] == 'editingRequired':
                        stxt += '审核不通过'
                    elif s['_id'] == 'delete':
                        stxt += '已删除'
                    elif s['_id'] == 'service-delete':
                        stxt += '系统删除'
                    else:
                        stxt += s['_id']
                    sL.append({'status': s['_id'], 'Count': s['Count'], 'statusTxt': stxt})


            if wd != '':
                words = re.compile(wd)

                filerList = []
                filerList.append({'subject':words})
                filerList.append({'productId':words})

                option['$or'] = filerList



            #print(option)
            totalCount = db.productList.find(option).count()

            productData = db.productList.find(option).sort(sortTxt,-1).limit(pageSize).skip((page-1)*pageSize)

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
            filterData['sort'] = sort
            filterData['create'] = create

            self.render('smt/product-list.html',productData = productData,pageInfo = pageInfo,filterData=filterData,userInfo={'account':user,'role':role})

            #self.render('index.html')

        else:
            #self.write("No Permission")
            self.render('error/message.html', msg={'Msg': 'No Permission', 'Code': 400,'Title':'无权限！','Link':'/'})


class SMTCheckOrderHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):

        storeId = self.get_argument('storeId','')
        status = self.get_argument('status','')
        url = apiServer+"/smt/api/checkOrder?storeId=%s&status=%s" % (storeId, status)
        request = HTTPRequest(url=url,method="GET",follow_redirects=False,request_timeout=3000)
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, request)
        try:
            result = json.loads(response.body)
        except Exception as e:
            result = {'success':False,'error':[{"storeId":storeId,'options':{'orderStatus':status},"errMsg":str(e),'data':response}]}
        self.write(result)
        self.finish()


class SMTCheckNewOrderHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):

        storeId = self.get_argument('storeId', '')
        url = apiServer+"/smt/api/checkNewOrder?" +urllib.urlencode({'storeId':storeId})
        request = HTTPRequest(url=url,method="GET",follow_redirects=False,request_timeout=30000)
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, request)
        result = json.loads(response.body)
        self.write(result)
        self.finish()

class SMTRefreshOrderStatusHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):

        items = self.get_argument('items', '')
        url = apiServer+"/smt/api/refreshOrderStatus?" +urllib.urlencode({'items':items})
        request = HTTPRequest(url=url,method="GET",follow_redirects=False,request_timeout=3000)
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, request)
        result = json.loads(response.body)
        self.write(result)
        self.finish()

class SMTRefreshOrderInfosHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):

        items = self.get_argument('items', '')
        url = apiServer+"/smt/api/refreshOrderInfos?" +urllib.urlencode({'items':items})
        request = HTTPRequest(url=url,method="GET",follow_redirects=False,request_timeout=3000)
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, request)
        result = json.loads(response.body)
        self.write(result)
        self.finish()


class SMTCheckProductHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):

        storeId = self.get_argument('storeId','')
        status = self.get_argument('status','onSelling')
        url = apiServer+"/smt/api/checkProduct?storeId=%s&status=%s" % (storeId, status)
        request = HTTPRequest(url=url,method="GET",follow_redirects=False,request_timeout=3000)
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, request)
        result = json.loads(response.body)
        self.write(result)
        self.finish()


class SMTRefreshProductStatusHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):

        items = self.get_argument('items', '')
        url = apiServer+"/smt/api/refreshProductStatus?" +urllib.urlencode({'items':items})
        request = HTTPRequest(url=url,method="GET",follow_redirects=False,request_timeout=3000)
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, request)
        result = json.loads(response.body)
        self.write(result)
        self.finish()

class SMTRefreshProductInfosHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):

        items = self.get_argument('items', '')
        url = apiServer+"/smt/api/refreshProductInfos?" +urllib.urlencode({'items':items})
        request = HTTPRequest(url=url,method="GET",follow_redirects=False,request_timeout=3000)
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, request)
        result = json.loads(response.body)
        self.write(result)
        self.finish()


class SMTRefreshNewProductInfosHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):

        storeId = self.get_argument('storeId', '')
        url = apiServer+"/smt/api/refreshNewProductInfos?" +urllib.urlencode({'storeId':storeId})
        request = HTTPRequest(url=url,method="GET",follow_redirects=False,request_timeout=30000)
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, request)
        result = json.loads(response.body)
        self.write(result)
        self.finish()
