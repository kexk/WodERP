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
                        pl = db.productList.find(
                            {'aeopAeProductSKUs': {'$exists': 0}, 'storeInfo.storeId': app['storeId']},
                            {'productId': 1}).limit(30)
                        for p in pl:
                            id = p['productId']
                            c = api.getProductById(id)
                            try:
                                d = json.loads(c)
                                productData = db.productList.find_one({'productId': id})

                                if d.has_key('success') and d['success']:
                                    d['productId'] = str(d['productId'])
                                    d['gmtModified'] = datetime.datetime.strptime(d['gmtModified'][:14], '%Y%m%d%H%M%S')
                                    d['wsOfflineDate'] = datetime.datetime.strptime(d['wsOfflineDate'][:14],
                                                                                    '%Y%m%d%H%M%S')
                                    d['gmtCreate'] = datetime.datetime.strptime(d['gmtCreate'][:14], '%Y%m%d%H%M%S')
                                    if d.has_key('couponStartDate'):
                                        d['couponStartDate'] = datetime.datetime.strptime(d['couponStartDate'][:14],
                                                                                          '%Y%m%d%H%M%S')
                                    if d.has_key('couponEndDate'):
                                        d['couponEndDate'] = datetime.datetime.strptime(d['couponEndDate'][:14],
                                                                                        '%Y%m%d%H%M%S')

                                    # 如果修改了标题,重新检查标题
                                    if productData['subject'] != d['subject']:
                                        d['checkTitleStatus'] = 'waitCheck'

                                    # print(newData)
                                    db.productList.update({'productId': id}, {'$set': d})
                                    data['count'] += 1
                                elif d.has_key('error_message'):
                                    if d['error_code'] == '10004000':
                                        db.productList.update({'productId': id},
                                                              {'$set': {'isDelete': 1, 'productStatusType': 'delete'}})
                                        data['count'] += 1
                                    data['error'].append({'id': id, 'errMsg': d['error_message']})

                            except Exception as e:
                                data['error'].append({'id': id, 'errMsg': str(e)})

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
