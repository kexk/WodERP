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
    #status:商品业务状态

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
                if '-K=' in p:
                    params['key'] = p.split('=')[1]

            if params.has_key('storeId') and params['storeId']!= '':

                mongo = MongoCase()
                mongo.connect()
                client = mongo.client
                db = client.woderp

                #print(params)

                app = db.appList.find_one({'storeId': params['storeId']})
                data['error'] = []
                data['count'] = 0
                if app != None:
                    api = ALIEXPRESS(app)
                    if api.status > 0:
                        # ol = db.orderList.find({key: {'$exists':0}, 'storeInfo.storeId': app['storeId']}, {'orderId': 1}).limit(pageSize)

                        pageSize = 50
                        key = ''
                        if params.has_key('key'):
                            key += params['key']
                        else:
                            key += 'receiptAddress'

                        updateFilter = {'storeInfo.storeId': app['storeId'],
                                        'updateTime': {'$lt': datetime.datetime.now() + datetime.timedelta(minutes=-15),
                                                       'orderStatus': {
                                                           '$in': ['WAIT_SELLER_SEND_GOODS', 'PLACE_ORDER_SUCCESS',
                                                                   'IN_CANCEL', 'SELLER_PART_SEND_GOODS','WAIT_SELLER_SEND_GOODS',
                                                                   'FUND_PROCESSING', 'IN_ISSUE', 'RISK_CONTROL']}}}
                        ol = db.orderList.find(
                            {'$or': [{key: {'$exists': 0}, 'storeInfo.storeId': app['storeId']}, updateFilter]},
                            {'orderId': 1}).limit(pageSize)
                        for o in ol:
                            id = o['orderId']
                            c = api.getOrderDetail(id)
                            if c != 'null':
                                orderInfo = json.loads(c)
                                orderData = db.orderList.find_one({'orderId': id})
                                newData = dict()
                                if not orderData.has_key('buyerInfo'):
                                    newData['buyerInfo'] = orderInfo['buyerInfo']
                                if not orderData.has_key('receiptAddress'):
                                    newData['receiptAddress'] = orderInfo['receiptAddress']
                                if not orderData.has_key('sellerOperatorLoginId'):
                                    newData['sellerOperatorLoginId'] = orderInfo['sellerOperatorLoginId']
                                if orderInfo.has_key('gmtPaySuccess'):
                                    newData['gmtPaySuccess'] = datetime.datetime.strptime(
                                        orderInfo['gmtPaySuccess'][:14], '%Y%m%d%H%M%S')
                                if orderInfo.has_key('gmtPaySuccess'):
                                    newData['gmtPayTime'] = datetime.datetime.strptime(orderInfo['gmtPaySuccess'][:14],
                                                                                       '%Y%m%d%H%M%S')
                                if not orderData.has_key('paymentType') and orderInfo.has_key('paymentType'):
                                    newData['paymentType'] = orderInfo['paymentType']
                                if not orderData.has_key('initOderAmount'):
                                    newData['initOderAmount'] = orderInfo['initOderAmount']
                                if not orderData.has_key('logisticsAmount'):
                                    newData['logisticsAmount'] = orderInfo['logisticsAmount']
                                if not orderData.has_key('orderAmount'):
                                    newData['orderAmount'] = orderInfo['orderAmount']
                                if not orderData.has_key('isPhone'):
                                    newData['isPhone'] = orderInfo['isPhone']

                                if not orderData.has_key('childOrderExtInfoList'):
                                    childOrderExtInfoList = orderInfo['childOrderExtInfoList']
                                    newChild = []
                                    for child in childOrderExtInfoList:
                                        child['productId'] = str(child['productId'])
                                        child['sku'] = json.loads(child['sku'])['sku']
                                        newChild.append(child)

                                    newData['childOrderExtInfoList'] = newChild

                                # 子订单包含状态
                                if not orderData.has_key('childOrderList'):
                                    childOrderList = orderInfo['childOrderList']
                                    newChild = []
                                    for child in childOrderList:
                                        child['id'] = str(child['id'])
                                        child['productId'] = str(child['productId'])
                                        child['productAttributes'] = json.loads(child['productAttributes'])
                                        newChild.append(child)

                                    newData['childOrderList'] = newChild

                                newData['issueInfo'] = orderInfo['issueInfo']
                                newData['issueStatus'] = orderInfo['issueStatus']
                                newData['loanInfo'] = orderInfo['loanInfo']
                                newData['logisticInfoList'] = orderInfo['logisticInfoList']
                                if orderInfo.has_key('logisticsStatus'):
                                    newData['logisticsStatus'] = orderInfo['logisticsStatus']
                                newData['oprLogDtoList'] = orderInfo['oprLogDtoList']
                                newData['orderMsgList'] = orderInfo['orderMsgList']
                                newData['orderStatus'] = orderInfo['orderStatus']
                                newData['frozenStatus'] = orderInfo['frozenStatus']
                                newData['fundStatus'] = orderInfo['fundStatus']
                                newData['gmtModified'] = orderInfo['gmtModified']

                                if newData['orderStatus'] == 'FINISH' or newData[
                                    'orderStatus'] == 'WAIT_BUYER_ACCEPT_GOODS' or newData[
                                    'orderStatus'] == 'FUND_PROCESSING':
                                    newData['timeoutLeftTime'] = None
                                    newData['leftSendGoodMin'] = None
                                    newData['leftSendGoodDay'] = None
                                    newData['leftSendGoodHour'] = None

                                # print(newData)
                                db.orderList.update({'orderId': id}, {'$set': newData})
                                data['count'] += 1

                            else:

                                data['error'].append({'id': id, 'errMsg': '找不到该订单'})


                    else:
                        data['error'].append({'storeId': app['storeId'], 'errMsg': '接口不可用'})

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
