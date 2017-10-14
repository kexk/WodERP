#coding:utf-8

from flask import Flask
from flask import request
from flask import jsonify

from apps.database.databaseCase import *
from apps.aliexpress.smtAPI import *
from apps.jingdong.jdAPI import *

import random
import datetime
import json


app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1 style="font-size:144px;text-align:center;">API</h1> '


@app.route('/smt/api/checkOrder')
def chekSMTOrder():
    storeId = request.args.get('storeId', '')
    status = request.args.get('status', '')

    data = dict()

    mongo = MongoCase()
    mongo.connect()
    client = mongo.client
    db = client.woderp

    appList = db.appList.find({'platform': 'aliexpress', 'apiInfo.status': 1})

    if storeId == '':
        # appKey = aList[random.randint(0,len(aList)-1)]
        app = appList[random.randint(0, appList.count() - 1)]
    else:
        app = db.appList.find_one({'storeId': storeId})

    data['error'] = []
    if app != None:

        api = ALIEXPRESS(app)

        total = 0
        addCount = 0
        updateCount = 0

        # statusList = ['WAIT_SELLER_SEND_GOODS','PLACE_ORDER_SUCCESS','IN_CANCEL','IN_ISSUE','RISK_CONTROL','WAIT_BUYER_ACCEPT_GOODS']
        statusList = status.split(',')


        for s in statusList:

            option = dict()
            option['pageSize'] = '50'
            option['page'] = '1'
            option['orderStatus'] = s

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
                        for sku in item['productList']:
                            sku['productId'] = str(sku['productId'])
                            sku['childId'] = str(sku['childId'])
                            sku['orderId'] = str(sku['orderId'])
                            sku['skuId'] = None
                            sku['skuAttr'] = None
                            sku['purchaseNo'] = None
                            sku['weight'] = None
                            sku['pickStatus'] = 0

                        newData = dict()
                        newData['productList'] = item['productList']
                        newData['orderStatus'] = item['orderStatus']
                        newData['frozenStatus'] = item['frozenStatus']
                        newData['issueStatus'] = item['issueStatus']
                        newData['fundStatus'] = item['fundStatus']
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

                        if not order.has_key('gmtPayTime') and item.has_key('gmtPayTime'):
                            newData['gmtPayTime'] = item['gmtPayTime']

                        db.orderList.update({'orderId': int(item['orderId'])}, {'$set': newData})

                        updateCount += 1
                    else:
                        item = od
                        item['orderId'] = str(item['orderId'])
                        item['createTime'] = datetime.datetime.now()
                        item['updateTime'] = updateTime
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

                        item['gmtCreate'] = datetime.datetime.strptime(od['gmtCreate'][:14], '%Y%m%d%H%M%S')

                        if od.has_key('gmtPayTime'):
                            item['gmtPayTime'] = datetime.datetime.strptime(od['gmtPayTime'][:14], '%Y%m%d%H%M%S')

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
                                    for sku in moreItem['productList']:
                                        sku['productId'] = str(sku['productId'])
                                        sku['childId'] = str(sku['childId'])
                                        sku['orderId'] = str(sku['orderId'])
                                        sku['skuId'] = None
                                        sku['skuAttr'] = None
                                        sku['purchaseNo'] = None
                                        sku['weight'] = None
                                        sku['pickStatus'] = 0

                                    newData = dict()
                                    newData['productList'] = moreItem['productList']
                                    newData['orderStatus'] = moreItem['orderStatus']
                                    newData['frozenStatus'] = moreItem['frozenStatus']
                                    newData['issueStatus'] = moreItem['issueStatus']
                                    newData['fundStatus'] = moreItem['fundStatus']
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

                                    if not order.has_key('gmtPayTime') and moreItem.has_key('gmtPayTime'):
                                        newData['gmtPayTime'] = moreItem['gmtPayTime']

                                    db.orderList.update({'orderId': int(moreItem['orderId'])}, {'$set': newData})

                                    updateCount += 1
                                else:
                                    moreItem = orderItem
                                    moreItem['orderId'] = str(moreItem['orderId'])
                                    moreItem['createTime'] = datetime.datetime.now()
                                    moreItem['updateTime'] = moreUpdateTime
                                    moreItem['storeInfo'] = {'storeId': app['storeId'], 'cnName': app['cnName'],
                                                             'enName': app['enName'], "operator": app["operator"],
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

                                    moreItem['gmtCreate'] = datetime.datetime.strptime(orderItem['gmtCreate'][:14],
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

                        except:
                            pass

            except Exception as e:
                print(e)
                data['error'].append({'storeId': app['storeId'],'errMsg':str(e),'options':option})

        data['success'] = True
        data['data'] = {"total": total, "addCount": addCount, 'updateCount': updateCount}

        return json.dumps(data, ensure_ascii=False)
    else:
        data['success'] = False
        data['error'].append({'storeId':storeId,'errMsg':'APP Unavailable','options':{'orderStatus':status}})
        return json.dumps(data, ensure_ascii=False)

@app.route('/smt/api/refreshOrderStatus')
def refreshSMTOrderStatus():
    data = dict()
    items = request.args.get('items', '')
    ol = json.loads(items)

    mongo = MongoCase()
    mongo.connect()
    client = mongo.client
    db = client.woderp

    data['error'] = []
    for (k,v) in  ol.items():
        app = db.appList.find_one({'storeId': k})
        if app != None:
            api = ALIEXPRESS(app)
            ids = v.strip(',').split(',')
            for id in ids:
                c = api.getOrderBaseInfo(id)
                try:
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
                except:
                    print(c)
                    data['error'].append({'id':id,'errMsg':str(c)})

    data['success'] = True
    data['errCount'] = len(data['error'])

    return json.dumps(data, ensure_ascii=False)


@app.route('/jd/api/checkOrder')
def CheckJDOrder():
    shopId = request.args.get('shop', '')
    status = request.args.get('status', '')
    mongo = MongoCase()
    mongo.connect()
    client = mongo.client
    db = client.jingdong

    appList = db.shopInfo.find()
    if shopId == '':
        app = appList[random.randint(0, appList.count() - 1)]
    else:
        app = db.shopInfo.find_one({'shopId': shopId})

    if app != None:
        api = JDAPI(app['apiInfo'])


        if status == '':
            statusList = ['WAIT_SELLER_STOCK_OUT','WAIT_GOODS_RECEIVE_CONFIRM','TRADE_CANCELED']
        else:
            statusList = ['WAIT_SELLER_STOCK_OUT']


        total = 0
        addCount = 0
        updateCount = 0

        for s in statusList:
            result = api.getOrderList(order_state=s)
            try:
                ol = result['order_search_response']['order_search']['order_info_list']
            except:
                ol = []
            for od in ol:
                item = od
                item['createTime'] = datetime.datetime.now()
                item['updateTime'] = None
                item['dealCompleteTime'] = None
                item['purchaseInfo'] = None
                item['dealRemark'] = None
                item['logisticsInfo'] = None
                item['shopId'] = app['shopId']
                item['platform'] = 'jingdong'
                if not item.has_key('payment_confirm_time'):
                    item['payment_confirm_time'] = None
                if not item.has_key('parent_order_id'):
                    item['parent_order_id'] = None
                if not item.has_key('pin'):
                    item['pin'] = None
                if not item.has_key('return_order'):
                    item['return_order'] = None
                if not item.has_key('order_state_remark'):
                    item['order_state_remark'] = None
                if not item.has_key('vender_remark'):
                    item['vender_remark'] = None

                item['dealStatus'] = 0
                item['stage'] = 0
                item['oprationLog'] = []

                for sku in item['item_info_list']:
                    sku['skuImg'] = None
                    sku['link'] = None
                    if not sku.has_key('product_no'):
                        sku['product_no'] = None
                    if not sku.has_key('outer_sku_id'):
                        sku['outer_sku_id'] = None
                    if not sku.has_key('ware_id'):
                        sku['ware_id'] = None

                if db.orderList.find({'order_id':item['order_id']}).count()>0:
                    updateCount += 1
                else:
                    db.orderList.insert(item)
                addCount += 1

                total +=1

        respon = {'success': True,"data":{"total":total,"addCount":addCount,'updateCount':updateCount}}
    else:
        respon = {'success':False}

    return json.dumps(respon, ensure_ascii=False)



if __name__ == '__main__':
    app.run()