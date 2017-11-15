#!/usr/bin/env python
#coding:utf-8
import os
import sys
import json
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from apps.database.databaseCase import *
from apps.aliexpress.smtAPI import *

if __name__ == "__main__":

    #storeId:店铺ID
    #status:订单状态
    #createDateStart:开始时间
    #createDateEnd:结束时间
    #参数格式：JSON字符串，使用单引号，
    #{'storeId': '3051010', 'status': 'WAIT_SELLER_SEND_GOODS,RISK_CONTROL,IN_CANCEL,PLACE_ORDER_SUCCESS,IN_ISSUE'}

    #BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    #print(sys.argv)
    #print(os.path.basename(__file__))
    #print(os.path.realpath(sys.argv[0]))
    #print(sys.argv[0].split('/')[-1])

    data = dict()
    data['msg'] = ''

    if os.path.basename(__file__) == sys.argv[0].split('/')[-1]:

        if len(sys.argv)>1:

            params = dict()

            for p in sys.argv[1:]:
                if '-I=' in p:
                    params['storeId'] = p.split('=')[1]

                elif '-S=' in p:
                    params['status'] = p.split('=')[1]

                elif '-T0=' in p:
                    params['createDateStart'] = p.split('=')[1]

                elif '-T1=' in p:
                    params['createDateEnd'] = p.split('=')[1]

            if params.has_key('storeId') and params['storeId']!= '':

                mongo = MongoCase()
                mongo.connect()
                client = mongo.client
                db = client.woderp

                #print(params)

                app = db.appList.find_one({'storeId': params['storeId']})
                data['error'] = []
                if app != None:
                    api = ALIEXPRESS(app)
                    if api.status > 0:

                        total = 0
                        addCount = 0
                        updateCount = 0

                        # statusList = ['WAIT_SELLER_SEND_GOODS','PLACE_ORDER_SUCCESS','IN_CANCEL','IN_ISSUE','RISK_CONTROL','WAIT_BUYER_ACCEPT_GOODS']
                        if params.has_key('status'):
                            statusList = params['status'].split(',')
                        else:
                            statusList = ['']

                        if params.has_key('createDateStart'):
                            createDateStart = params['createDateStart']
                        else:
                            createDateStart = ''
                        if params.has_key('createDateEnd'):
                            createDateEnd = params['createDateEnd']
                        else:
                            createDateEnd = ''

                        for s in statusList:

                            option = dict()
                            option['pageSize'] = '50'
                            option['page'] = '1'
                            option['orderStatus'] = s

                            if s == 'WAIT_BUYER_ACCEPT_GOODS' and createDateStart == '':
                                option['createDateStart'] = (
                                datetime.datetime.now() + datetime.timedelta(days=-10)).strftime('%Y-%m-%d %H:%M:%S')
                                option['createDateEnd'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                option['createDateStart'] = createDateStart
                                option['createDateEnd'] = createDateEnd

                            c = api.getOrderList(option)

                            try:
                                result = json.loads(c)

                                ol = result['orderList']
                                total += result['totalItem']

                                updateTime = datetime.datetime.now()
                                for od in ol:

                                    order = db.orderList.find_one({'orderId': str(od['orderId'])})
                                    if order:

                                        item = od

                                        newData = dict()
                                        newData['orderStatus'] = item['orderStatus']
                                        newData['frozenStatus'] = item['frozenStatus']
                                        newData['issueStatus'] = item['issueStatus']
                                        newData['fundStatus'] = item['fundStatus']
                                        if item.has_key('logisticsStatus'):
                                            newData['logisticsStatus'] = item['logisticsStatus']
                                        newData['updateTime'] = updateTime
                                        if item.has_key('timeoutLeftTime'):
                                            newData['timeoutLeftTime'] = item['timeoutLeftTime']
                                        else:
                                            newData['timeoutLeftTime'] = None
                                        if item.has_key('leftSendGoodMin'):
                                            newData['leftSendGoodMin'] = item['leftSendGoodMin']
                                        elif order.has_key('leftSendGoodMin'):
                                            newData['leftSendGoodMin'] = None
                                        if item.has_key('leftSendGoodHour'):
                                            newData['leftSendGoodHour'] = item['leftSendGoodHour']
                                        elif order.has_key('leftSendGoodHour'):
                                            newData['leftSendGoodHour'] = None
                                        if item.has_key('leftSendGoodDay'):
                                            newData['leftSendGoodDay'] = item['leftSendGoodDay']
                                        elif order.has_key('leftSendGoodDay'):
                                            newData['leftSendGoodDay'] = None

                                        if item.has_key('memo'):
                                            newData['memo'] = item['memo']

                                        if item.has_key('gmtPayTime'):
                                            newData['gmtPayTime'] = datetime.datetime.strptime(item['gmtPayTime'][:14],
                                                                                               '%Y%m%d%H%M%S')

                                        db.orderList.update({'orderId': str(item['orderId'])}, {'$set': newData})

                                        # print(newData)

                                        updateCount += 1
                                    else:
                                        item = od
                                        item['orderId'] = str(item['orderId'])
                                        item['createTime'] = datetime.datetime.now()
                                        item['updateTime'] = updateTime
                                        item['apiStoreID'] = app['apiStoreID']
                                        item['storeInfo'] = {'storeId': app['storeId'], 'cnName': app['cnName'],
                                                             'enName': app['enName'], "operator": app["operator"],
                                                             'dealPeron': app['dealPeron']}
                                        item['platform'] = app['platform']

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

                                        item['gmtCreate'] = datetime.datetime.strptime(od['gmtCreate'][:14],
                                                                                       '%Y%m%d%H%M%S')

                                        if od.has_key('gmtPayTime'):
                                            item['gmtPayTime'] = datetime.datetime.strptime(od['gmtPayTime'][:14],
                                                                                            '%Y%m%d%H%M%S')

                                        for sku in item['productList']:
                                            sku['productId'] = str(sku['productId'])
                                            sku['childId'] = str(sku['childId'])
                                            sku['orderId'] = str(sku['orderId'])
                                            sku['skuId'] = None
                                            sku['skuAttr'] = None
                                            sku['purchaseNo'] = None
                                            sku['weight'] = None
                                            sku['pickStatus'] = 0

                                        db.orderList.insert(item)
                                        addCount += 1

                                if int(result['totalItem']) > int(option['pageSize']):
                                    totalPage = int(result['totalItem']) / int(option['pageSize'])
                                    mod = int(result['totalItem']) % int(option['pageSize'])
                                    if mod > 0:
                                        totalPage += 1

                                    pl = range(2, totalPage + 1)
                                    for page in pl:
                                        # print(page)
                                        option['page'] = str(page)
                                        # print(option)
                                        m = api.getOrderList(option)
                                        moreUpdateTime = datetime.datetime.now()
                                        try:
                                            moreOrder = json.loads(m)
                                            moreOrderList = moreOrder['orderList']

                                            for orderItem in moreOrderList:

                                                order = db.orderList.find_one({'orderId': str(orderItem['orderId'])})
                                                if order:

                                                    moreItem = orderItem

                                                    newData = dict()
                                                    newData['orderStatus'] = moreItem['orderStatus']
                                                    newData['frozenStatus'] = moreItem['frozenStatus']
                                                    newData['issueStatus'] = moreItem['issueStatus']
                                                    newData['fundStatus'] = moreItem['fundStatus']
                                                    if moreItem.has_key('logisticsStatus'):
                                                        newData['logisticsStatus'] = moreItem['logisticsStatus']
                                                    newData['updateTime'] = moreUpdateTime
                                                    if moreItem.has_key('timeoutLeftTime'):
                                                        newData['timeoutLeftTime'] = moreItem['timeoutLeftTime']
                                                    else:
                                                        newData['timeoutLeftTime'] = None
                                                    if moreItem.has_key('leftSendGoodMin'):
                                                        newData['leftSendGoodMin'] = moreItem['leftSendGoodMin']
                                                    elif order.has_key('leftSendGoodMin'):
                                                        newData['leftSendGoodMin'] = None
                                                    if moreItem.has_key('leftSendGoodHour'):
                                                        newData['leftSendGoodHour'] = moreItem['leftSendGoodHour']
                                                    elif order.has_key('leftSendGoodHour'):
                                                        newData['leftSendGoodHour'] = None
                                                    if moreItem.has_key('leftSendGoodDay'):
                                                        newData['leftSendGoodDay'] = moreItem['leftSendGoodDay']
                                                    elif order.has_key('leftSendGoodDay'):
                                                        newData['leftSendGoodDay'] = None

                                                    if moreItem.has_key('memo'):
                                                        newData['memo'] = moreItem['memo']

                                                    if moreItem.has_key('gmtPayTime'):
                                                        newData['gmtPayTime'] = datetime.datetime.strptime(
                                                            moreItem['gmtPayTime'][:14], '%Y%m%d%H%M%S')

                                                    db.orderList.update({'orderId': str(moreItem['orderId'])},
                                                                        {'$set': newData})

                                                    updateCount += 1
                                                else:
                                                    moreItem = orderItem
                                                    moreItem['orderId'] = str(moreItem['orderId'])
                                                    moreItem['createTime'] = datetime.datetime.now()
                                                    moreItem['updateTime'] = moreUpdateTime
                                                    moreItem['apiStoreID'] = app['apiStoreID']
                                                    moreItem['storeInfo'] = {'storeId': app['storeId'],
                                                                             'cnName': app['cnName'],
                                                                             'enName': app['enName'],
                                                                             "operator": app["operator"],
                                                                             'dealPeron': app['dealPeron']}
                                                    moreItem['platform'] = app['platform']

                                                    moreItem['dealStatus'] = 'WAIT_SYSTEM_CHECK'
                                                    moreItem['oprationLog'] = []
                                                    moreItem['weight'] = None
                                                    moreItem['totalCost'] = None
                                                    moreItem['totalProfit'] = None
                                                    moreItem['isLock'] = 0
                                                    moreItem['type'] = 0
                                                    moreItem['isShelve'] = 0
                                                    moreItem['isShelve'] = 0
                                                    moreItem['errorMsg'] = None
                                                    moreItem['isMakeup'] = 0
                                                    moreItem['reSendReason'] = 0
                                                    moreItem['isMergeOrder'] = 0
                                                    moreItem['isSplitOrder'] = 0
                                                    moreItem['hasMessage'] = 0
                                                    moreItem['isDelivery'] = 0
                                                    moreItem['checkName'] = 0
                                                    moreItem['orderMemo'] = []
                                                    moreItem['labels'] = []
                                                    moreItem['pickStatus'] = 0

                                                    moreItem['gmtCreate'] = datetime.datetime.strptime(
                                                        orderItem['gmtCreate'][:14],
                                                        '%Y%m%d%H%M%S')

                                                    if orderItem.has_key('gmtPayTime'):
                                                        moreItem['gmtPayTime'] = datetime.datetime.strptime(
                                                            orderItem['gmtPayTime'][:14],
                                                            '%Y%m%d%H%M%S')

                                                    for sku in moreItem['productList']:
                                                        sku['productId'] = str(sku['productId'])
                                                        sku['childId'] = str(sku['childId'])
                                                        sku['orderId'] = str(sku['orderId'])
                                                        sku['skuId'] = None
                                                        sku['skuAttr'] = None
                                                        sku['purchaseNo'] = None
                                                        sku['weight'] = None
                                                        sku['pickStatus'] = 0

                                                    db.orderList.insert(moreItem)
                                                    addCount += 1

                                        except Exception as e:
                                            data['error'].append(
                                                {'storeId': app['storeId'], 'errMsg': str(e), 'data': m,
                                                 'options': option})

                            except Exception as e:
                                # print(e)
                                data['error'].append(
                                    {'storeId': app['storeId'], 'errMsg': str(e), 'data': {}, 'options': option})

                        data['success'] = True
                        data['data'] = {"total": total, "addCount": addCount, 'updateCount': updateCount}

                    else:
                        data['success'] = False
                        data['error'].append(
                            {'storeId': app['storeId'], 'errMsg': 'APP Unavailable', 'options': {'orderStatus': params}})

                else:
                    data['success'] = False
                    data['msg'] = '店铺查询不到'
            else:
                data['success'] = False
                data['msg'] = '参数店铺ID不合法'
        else:
            data['success'] = False
            data['msg'] = '缺少参数'
    else:
        data['success'] = False
        data['msg'] = '方法不匹配'

    print(data)
