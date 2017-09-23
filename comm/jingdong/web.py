#coding:utf-8


from base import BaseHandler

from comm.jingdong.jdAPI import *
from comm.database.databaseCase import *
import json



class CheckOrderHandler(BaseHandler):
    def get(self):

        #result = o.getOrderList(order_state='WAIT_GOODS_RECEIVE_CONFIRM')

        appKey = self.get_argument('appKey')

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client
        db = client.jingdong

        app = db.apiInfo.find_one({'app_key':appKey})

        if app != None:

            dberp = client.woderp

            api = JDAPI(app)
            result = api.getOrderList(order_state='WAIT_SELLER_STOCK_OUT')

            ol = result['order_search_response']['order_search']['order_info_list']
            total = 0
            addCount = 0
            for od in ol:
                item = od
                item['createTime'] = datetime.datetime.now()
                item['updateTime'] = None
                item['dealCompleteTime'] = None
                item['purchaseInfo'] = None
                item['dealRemark'] = None
                item['logisticsInfo'] = None
                item['shopId'] = '163184'
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

                try:
                    dberp.orderList.insert(item)
                    addCount += 1
                except Exception as e:
                    print(e)

                total +=1

            respon = {'success': True,"data":{"total":total,"addCount":addCount}}

            self.write(json.dumps(respon,ensure_ascii=False))
        else:
            self.write(json.dumps({'success':False},ensure_ascii=False))


class CheckSkuHandler(BaseHandler):

    def get(self):

        appKey = self.get_argument('appKey','40BF94D17B3F69D29294F645AD10BFC2')
        sku = self.get_argument('sku','')

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client
        db = client.jingdong

        app = db.apiInfo.find_one({'app_key':appKey})


        data = dict()
        if sku != '' and app != None:

            dberp = client.woderp

            api = JDAPI(app)
            result = api.searchSkuList(option={'page_size':'100','skuId':sku,'field':'wareId,skuId,status,jdPrice,outerId,categoryId,logo,skuName,stockNum,wareTitle,created'})
            sl = result['jingdong_sku_read_searchSkuList_responce']['page']['data']
            for s in sl:
                item = s
                item['createTime'] = datetime.datetime.now()
                item['updateTime'] = None
                item['shopId'] = '163184'
                item['platform'] = 'jingdong'
                item['stage'] = 0
                item['oprationLog'] = []
                item['skuId'] = str(s['skuId'])
                item['wareId'] = str(s['wareId'])

                try:
                    dberp.skuList.insert(item)
                except Exception as e:
                    print(e)

            data['success'] = True

        else:
            data['success'] = False

        self.write(json.dumps(data,ensure_ascii=False))