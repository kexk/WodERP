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

                elif '-S=' in p:
                    params['status'] = p.split('=')[1]

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

                        # statusList = ['onSelling','offline','auditing','editingRequired']
                        if params.has_key('status'):
                            statusList = params['status'].split(',')
                        else:
                            statusList = ['onSelling']

                        for s in statusList:

                            option = dict()
                            option['pageSize'] = '100'
                            option['currentPage'] = '1'
                            option['productStatusType'] = s

                            c = api.getProductInfoList(option)

                            try:
                                result = json.loads(c)

                                if result['productCount'] > 0:

                                    pl = result['aeopAEProductDisplayDTOList']
                                    total += result['productCount']

                                    updateTime = datetime.datetime.now()

                                    # db.productList.update({},{'$set':{'isDelete':1}})

                                    for pd in pl:

                                        product = db.productList.find_one({'productId': str(pd['productId'])})
                                        if product:

                                            newData = pd
                                            newData['productId'] = str(pd['productId'])
                                            newData['isDelete'] = 0
                                            newData['productStatusType'] = s
                                            newData['updateTime'] = updateTime

                                            if product['subject'] != pd['subject']:
                                                newData['checkTitleStatus'] = 'waitCheck'

                                            newData['wsOfflineDate'] = datetime.datetime.strptime(
                                                pd['wsOfflineDate'][:14], '%Y%m%d%H%M%S')
                                            newData['gmtCreate'] = datetime.datetime.strptime(pd['gmtCreate'][:14],
                                                                                              '%Y%m%d%H%M%S')
                                            newData['gmtModified'] = datetime.datetime.strptime(pd['gmtModified'][:14],
                                                                                                '%Y%m%d%H%M%S')

                                            db.productList.update({'productId': str(pd['productId'])},
                                                                  {'$set': newData})

                                            # print(newData)

                                            updateCount += 1
                                        else:
                                            item = pd
                                            item['productId'] = str(pd['productId'])
                                            item['createTime'] = datetime.datetime.now()
                                            item['updateTime'] = updateTime
                                            item['apiStoreID'] = app['apiStoreID']
                                            item['storeInfo'] = {'storeId': app['storeId'], 'cnName': app['cnName'],
                                                                 'enName': app['enName'], "operator": app["operator"],
                                                                 'dealPeron': app['dealPeron']}
                                            item['platform'] = app['platform']

                                            item['isDelete'] = 0
                                            item['productStatusType'] = s
                                            item['checkTitleStatus'] = 'waitCheck'

                                            item['labels'] = []
                                            item['riskWords'] = []
                                            item['isNew'] = 1

                                            item['gmtCreate'] = datetime.datetime.strptime(pd['gmtCreate'][:14],
                                                                                           '%Y%m%d%H%M%S')
                                            item['gmtModified'] = datetime.datetime.strptime(pd['gmtModified'][:14],
                                                                                             '%Y%m%d%H%M%S')
                                            item['wsOfflineDate'] = datetime.datetime.strptime(pd['wsOfflineDate'][:14],
                                                                                               '%Y%m%d%H%M%S')

                                            db.productList.insert(item)
                                            addCount += 1

                                    if int(result['productCount']) > int(option['pageSize']):
                                        totalPage = int(result['totalPage'])

                                        pl = range(2, totalPage + 1)
                                        for page in pl:
                                            option['currentPage'] = str(page)
                                            m = api.getProductInfoList(option)
                                            moreUpdateTime = datetime.datetime.now()
                                            try:
                                                moreProduct = json.loads(m)

                                                moreProductList = moreProduct['aeopAEProductDisplayDTOList']

                                                for productItem in moreProductList:

                                                    mp = db.productList.find_one(
                                                        {'productId': str(productItem['productId'])})
                                                    if mp:

                                                        newData = productItem
                                                        newData['productId'] = str(productItem['productId'])
                                                        newData['isDelete'] = 0
                                                        newData['productStatusType'] = s
                                                        newData['updateTime'] = moreUpdateTime

                                                        if mp['subject'] != productItem['subject']:
                                                            newData['checkTitleStatus'] = 'waitCheck'

                                                        newData['wsOfflineDate'] = datetime.datetime.strptime(
                                                            productItem['wsOfflineDate'][:14], '%Y%m%d%H%M%S')
                                                        newData['gmtCreate'] = datetime.datetime.strptime(
                                                            productItem['gmtCreate'][:14], '%Y%m%d%H%M%S')
                                                        newData['gmtModified'] = datetime.datetime.strptime(
                                                            productItem['gmtModified'][:14], '%Y%m%d%H%M%S')

                                                        db.productList.update(
                                                            {'productId': str(productItem['productId'])},
                                                            {'$set': newData})

                                                        updateCount += 1
                                                    else:
                                                        moreItem = productItem
                                                        moreItem['productId'] = str(moreItem['productId'])

                                                        moreItem['createTime'] = datetime.datetime.now()
                                                        moreItem['updateTime'] = moreUpdateTime
                                                        moreItem['apiStoreID'] = app['apiStoreID']
                                                        moreItem['storeInfo'] = {'storeId': app['storeId'],
                                                                                 'cnName': app['cnName'],
                                                                                 'enName': app['enName'],
                                                                                 "operator": app["operator"],
                                                                                 'dealPeron': app['dealPeron']}
                                                        moreItem['platform'] = app['platform']

                                                        moreItem['isDelete'] = 0
                                                        moreItem['productStatusType'] = s
                                                        moreItem['checkTitleStatus'] = 'waitCheck'

                                                        moreItem['labels'] = []
                                                        moreItem['riskWords'] = []
                                                        moreItem['isNew'] = 1

                                                        moreItem['gmtCreate'] = datetime.datetime.strptime(
                                                            productItem['gmtCreate'][:14], '%Y%m%d%H%M%S')
                                                        moreItem['gmtModified'] = datetime.datetime.strptime(
                                                            productItem['gmtModified'][:14], '%Y%m%d%H%M%S')
                                                        moreItem['wsOfflineDate'] = datetime.datetime.strptime(
                                                            productItem['wsOfflineDate'][:14], '%Y%m%d%H%M%S')

                                                        db.productList.insert(moreItem)
                                                        addCount += 1

                                            except Exception as e:
                                                # print(e)
                                                data['error'].append(
                                                    {'storeId': app['storeId'], 'errMsg': str(e), 'options': option})


                            except Exception as e:
                                # print(e)
                                data['error'].append({'storeId': app['storeId'], 'errMsg': str(e), 'options': option})

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
