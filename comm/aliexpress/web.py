#coding:utf-8


from base import BaseHandler

from comm.aliexpress.smtAPI import *
from comm.database.databaseCase import *
import json
import datetime


class CheckSmtOrderHandler(BaseHandler):
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
            c = api.getOrderList()

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