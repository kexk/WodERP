#coding:utf-8
import os.path
import re

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
from tornado.options import define, options


from comm.jingdong.jdAPI import *

from comm.alibaba.alibabaAPI import *
from comm.database.databaseCase import *

import datetime
from bson import objectid
import hashlib
import json

define("port", default=9999, help="run on the given port", type=int)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("email")

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('error/404.html')
        elif status_code == 500:
            self.render('error/500.html')
        else:
            self.write('error:' + str(status_code))


class IndexHandler(BaseHandler):

    #@tornado.web.authenticated
    def get(self):
        greeting = self.get_argument('greeting', 'Hello')
        greeting += ', friendly user! '


        user = self.current_user
        role = self.get_secure_cookie("role") if self.get_secure_cookie("role") else 'None'


        self.render('index.html',greeting=greeting,userInfo={'account':user,'role':role})

        #self.render('index.html')

    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error.\n" % status_code)


class LoginHandler(BaseHandler):

    def get(self):
        user = self.current_user
        referer = self.get_argument('next','/')
        if user:
            self.redirect(referer)
        else:
            self.render('login.html',referer=referer)


    def post(self):

        email = self.get_argument('email','')
        password = self.get_argument('password','')

        if email == '' or password == '':
            self.render('error.html',msg=u'Email 密码 不能为空!')

        else:

            mongo = MongoCase()
            mongo.connect()
            client = mongo.client
            db = client.jingdong
            user = db.user.find({"account":email})
            if user.count()<1:
                self.render('error.html',msg=u'Email 不存在')
            else:
                m = hashlib.md5()
                m.update(password)
                sign = m.hexdigest()
                if user[0]['password'] != sign:
                    self.render('error.html',msg=u'密码错误')

                else:
                    self.set_secure_cookie("email", email)
                    if user[0]['isSupper']:
                        self.set_secure_cookie("role", 'Admin')
                        #self.redirect('/admin')
                    else:
                        self.set_secure_cookie("role", 'User')

                    if user[0]['isActive']:
                            self.redirect(self.get_argument('next','/'))
                    else:
                        self.render('error.html',msg=u'未激活用户,重新申请激活 '+u'>> <a href="/profile">修改资料</a>')


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("email")
        self.clear_cookie("role")
        self.redirect('/')


class AuthHandler(BaseHandler):
    def get(self):
        code = self.get_argument('code', '')

        self.render('index.html')



class OrderListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):

        user = self.current_user
        role = self.get_secure_cookie("role") if self.get_secure_cookie("role") else 'None'

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client

        db = client.jingdong

        pageSize = 50

        status = self.get_argument('status','')
        wd = self.get_argument('wd','')


        try:
            page = int(self.get_argument('page',1))
        except:
            page = 1

        #totalCount = db.orderList.find({"order_state":"WAIT_SELLER_STOCK_OUT"}).count()
        option = {}
        if status == '0':
            option['order_state'] = 'WAIT_SELLER_STOCK_OUT'
        elif status == '1':
            option['order_state'] = 'WAIT_GOODS_RECEIVE_CONFIRM'


        if wd != '':
            words = re.compile(wd)

            filerList = []
            filerList.append({'item_info_list.sku_name':words})
            filerList.append({'item_info_list.sku_id':words})
            filerList.append({'order_id':words})
            filerList.append({'consignee_info.fullname':words})
            filerList.append({'consignee_info.mobile':words})
            filerList.append({'consignee_info.telephone':words})
            filerList.append({'logisticsInfo.waybill':words})

            option['$or'] = filerList



        totalCount = db.orderList.find(option).count()

        orderList = db.orderList.find(option).sort("order_start_time",-1).limit(pageSize).skip((page-1)*pageSize)

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

        self.render('order-list.html',orderList = orderList,pageInfo = pageInfo,filterData=filterData,userInfo={'account':user,'role':role})

        #self.render('index.html')

    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error.\n" % status_code)



class PurchaseListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):

        user = self.current_user
        role = self.get_secure_cookie("role") if self.get_secure_cookie("role") else 'None'

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client

        db = client.jingdong

        pageSize = 50

        status = self.get_argument('status','')
        wd = self.get_argument('wd','')


        try:
            page = int(self.get_argument('page',1))
        except:
            page = 1

        option = {}
        if status == '0':
            option['status'] = 'waitsellersend'
        elif status == '1':
            option['status'] = 'waitbuyerreceive'


        if wd != '':
            words = re.compile(wd)

            filerList = []
            filerList.append({'orderEntries.productName':words})
            filerList.append({'toFullName':words})
            filerList.append({'toMobile':words})
            filerList.append({'buyerAccount':words})
            filerList.append({'sellerCompanyName':words})
            filerList.append({'logistics.toContact':words})
            filerList.append({'logistics.logisticsBillNo':words})
            try:
                filerList.append({'id':int(wd)})
            except:
                pass

            option['$or'] = filerList


        totalCount = db.purchaseList.find(option).count()

        purchaseList = db.purchaseList.find(option).sort("gmtCreate",-1).limit(pageSize).skip((page-1)*pageSize)

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

        self.render('purchase-list.html',purchaseList = purchaseList,pageInfo = pageInfo,filterData=filterData,userInfo={'account':user,'role':role})

        #self.render('index.html')

    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error.\n" % status_code)


class PurchaseOrderListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):

        user = self.current_user
        role = self.get_secure_cookie("role") if self.get_secure_cookie("role") else 'None'

        data = dict()
        try:
            page = int(self.get_argument('pageNO','1'))-1
        except:
            page = 0
        data['pageNO'] = page
        data['orderStatus'] = ''
        data['createStartTime'] = ''
        data['createEndTime'] = ''


        self.render('purchase-list.html',data=data,userInfo={'account':user,'role':role})

        #self.render('index.html')

    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error.\n" % status_code)


class APIGetPurchaseListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):

        data = dict()

        pageSize = 20

        orderStatus = self.get_argument('orderStatus','')
        pageNO = self.get_argument('pageNO','1')
        createStartTime = self.get_argument('createStartTime','')
        createEndTime = self.get_argument('createEndTime','')


        option = {'pageNO':pageNO}
        if orderStatus != '':
            option['orderStatus'] = orderStatus
        if createStartTime != '':
            option['createStartTime'] = createStartTime
        else:
            option['createStartTime'] = (datetime.datetime.now()+datetime.timedelta(days=-2)).strftime('%Y-%m-%d %H:%M:%S')
        if createEndTime != '':
            option['createEndTime'] = createEndTime


        api = ALIBABA()

        d = json.loads(api.getOrderList(option))

        if d.has_key('result') and d['result']['success']:

            data['orderList'] = d['result']['toReturn']
            data['success'] = True
            data['total'] = d['result']['total']

            totalPage = int(data['total']) / pageSize
            mod = int(data['total']) % pageSize

            if mod > 0:
                totalPage += 1

            data["page"] = int(pageNO)

            if data["page"] >= 9:
                if data["page"] <= totalPage - 9:
                    pageList = range(data["page"] - 3, data["page"] + 4)
                    pageItems = [1, '...'] + pageList + ['...', totalPage]
                else:
                    pageList = range(totalPage - 7, totalPage + 1)
                    pageItems = [1, '...'] + pageList
            else:
                if totalPage <= 12:
                    pageItems = range(1, totalPage + 1)
                else:
                    pageList = range(1, 10)
                    pageItems = pageList + ['...', totalPage]

            data["PageItem"] = '<li><a href="javascript:"><i class="fa fa-chevron-left"></i></a></li>'

            for pg in pageItems:
                html = '<li'
                if data["page"] == pg:
                    html += ' class="active"'

                html += '>'
                html += '<a href="javascript:" data-val="%s" class="pageItem">%s</a></li>' % (pg, pg)


                data["PageItem"] += html

            data["PageItem"] += '<li><a href="javascript:"><i class="fa fa-chevron-right"></i></a></li>'

            num0 = len(data['orderList'])

            if num0 > 0:
                i0 = int(pageSize) * (int(pageNO) - 1) + 1
                i1 = int(pageSize) * (int(pageNO) - 1) + num0
            else:
                i0 = 0
                i1 = 0

            data["PageTxt"] = {'start':i0,'end':i1,'total':int(data['total'])}

        else:
            data['success'] = False

        self.set_header('Content-Type', 'application/json; charset=UTF-8')

        self.write(json.dumps(data, ensure_ascii=False))


    def write_error(self, status_code, **kwargs):
        data = dict()
        data['success'] = False
        data['errCode'] = status_code
        self.write(tornado.escape.json_encode(data))



class CheckSkuHandler(BaseHandler):

    def get(self):
        mongo = MongoCase()
        mongo.connect()
        client = mongo.client
        db = client.jingdong


        data = dict()
        sku = self.get_argument('sku','')
        if sku != '':
            app = JDAPI()
            result = app.searchSkuList(option={'page_size':'100','skuId':sku,'field':'wareId,skuId,status,jdPrice,outerId,categoryId,logo,skuName,stockNum,wareTitle,created'})
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
                    db.skuList.insert(item)
                except Exception as e:
                    print(e)

            data['success'] = True

        else:
            data['success'] = False

        respon = data
        respon_json = tornado.escape.json_encode(respon)
        self.write(respon_json)


class ChcekOrderInfoHanlder(BaseHandler):

    def get(self):
        data = dict()
        orderId = self.get_argument('orderId', '')
        if orderId != '':
            mongo = MongoCase()
            mongo.connect()
            client = mongo.client
            db = client.jingdong
            app = JDAPI()
            result = app.getOrderDetail(order_id=orderId,
                                      option={"optional_fields": "order_state,pin,waybill,logistics_id,modified,return_order,order_state_remark,vender_remark,payment_confirm_time"})
            orderInfo = result['order_get_response']['order']['orderInfo']

            item = dict()

            if orderInfo["pin"] != '':
                item['pin'] = orderInfo["pin"]

            logistics = dict()
            if orderInfo["logistics_id"] != '':
                logistics['logistics_id'] = orderInfo["logistics_id"]
                logistics['waybill'] = orderInfo["waybill"]
            if logistics != {}:
                item['logisticsInfo'] = logistics
                item['dealStatus'] = 3
            item['modified'] = orderInfo['modified']
            item['order_state'] = orderInfo['order_state']
            item['return_order'] = orderInfo['return_order']
            item['order_state_remark'] = orderInfo['order_state_remark']
            item['vender_remark'] = orderInfo['vender_remark']
            item['payment_confirm_time'] = orderInfo['payment_confirm_time']
            item['updateTime'] = datetime.datetime.now()

            db.orderList.update({"order_id": orderId}, {'$set': item})

            data['success'] = True
        else:
            data['success'] = False

        respon = data
        respon_json = tornado.escape.json_encode(respon)
        self.write(respon_json)



class GetOrderItemsHandler(BaseHandler):

    def get(self):
        data = dict()
        orderId = self.get_argument('orderId','')

        data['items'] = []
        data['purchaseInfo'] = []
        if orderId != '':
            mongo = MongoCase()
            mongo.connect()
            client = mongo.client
            db = client.jingdong


            item = db.orderList.find_one({"order_id":orderId},{"item_info_list":1,"purchaseInfo":1})

            if item != None:


                if item['purchaseInfo']!=None:
                    for purchase in item['purchaseInfo']:
                        purchase['createDate'] = str(purchase['createDate'])
                        data['purchaseInfo'].append(purchase)

                for sku in item['item_info_list']:
                    foo = db.skuList.find_one({"skuId":sku['sku_id']},{"logo":1})



                    for p in data['purchaseInfo']:
                        for s in p['purchaseItems']:
                            if s['sku_id'] == sku['sku_id']:
                                sku['link'] = s['link']


                    if sku['skuImg']==None and foo != None:
                        sku['skuImg'] = foo['logo']
                        db.orderList.update({"item_info_list.sku_id":sku['sku_id']},{"$set":{"item_info_list.$.skuImg":sku['skuImg']}})

                    data['items'].append(sku)


        respon_json = tornado.escape.json_encode(data)
        self.write(respon_json)



class GetSkuImageHandler(BaseHandler):
    def get(self):

        skuId = self.get_argument('skuId','')

        mark = 0
        imgUrl = ''
        if skuId != '':
            mongo = MongoCase()
            mongo.connect()
            client = mongo.client
            db = client.jingdong
            item = db.skuList.find({"skuId":skuId},{"logo":1})
            if item.count()>0:
                imgUrl += item[0]['logo']
                db.orderList.update({"item_info_list.sku_id":skuId,"item_info_list.skuImg":None},{"$set":{"item_info_list.$.skuImg":item[0]['logo']}})


        if imgUrl == '':
            imgUrl += 'jfs/t3271/88/7808807198/85040/49d5cf69/58bccd95Nd1b090a7.jpg'
            mark += 1

        respon = {'imgUrl': imgUrl,'mark':mark}
        respon_json = tornado.escape.json_encode(respon)
        self.write(respon_json)


class CheckOrderHandler(BaseHandler):
    def get(self):
        app = JDAPI()
        result = app.getOrderList(order_state='WAIT_SELLER_STOCK_OUT')
        #result = o.getOrderList(order_state='WAIT_GOODS_RECEIVE_CONFIRM')
        mongo = MongoCase()
        mongo.connect()
        client = mongo.client
        db = client.jingdong
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
                db.orderList.insert(item)
                addCount += 1
            except Exception as e:
                print(e)

            total +=1

        respon = {'success': True,"data":{"total":total,"addCount":addCount}}
        respon_json = tornado.escape.json_encode(respon)
        self.write(respon_json)


class CheckPurchaseHandler(BaseHandler):
    def get(self):

        orderStatus = self.get_argument('orderStatus','')
        pageNO = self.get_argument('pageNO','1')
        createStartTime = self.get_argument('createStartTime','')
        createEndTime = self.get_argument('createEndTime','')

        option = {'pageNO':pageNO}
        if orderStatus != '':
            option['orderStatus'] = orderStatus
        if createStartTime != '':
            option['createStartTime'] = createStartTime
        else:
            option['createStartTime'] = (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y-%m-%d %H:%M:%S')
        if createEndTime != '':
            option['createEndTime'] = createEndTime
        else:
            option['createEndTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


        api = ALIBABA()

        d = json.loads(api.getOrderList(option))

        if d.has_key('result') and d['result']['success']:
            mongo = MongoCase()
            mongo.connect()
            client = mongo.client
            db = client.jingdong

            ol = d['result']['toReturn']

            total = 0
            addCount = 0

            for od in ol:
                item = od
                item['createTime'] = datetime.datetime.now()
                item['updateTime'] = None
                item['buyerAccount'] = 'tj18690821588'
                item['dealCompleteTime'] = None
                item['dealRemark'] = None


                item['dealStatus'] = 0
                item['stage'] = 0
                item['oprationLog'] = []

                try:
                    db.purchaseList.insert(item)
                    addCount += 1
                except Exception as e:
                    print(e)

                total +=1

            respon = {'success': True,"data":{"total":total,"addCount":addCount}}
            respon_json = tornado.escape.json_encode(respon)
            self.write(respon_json)

        else:
            respon = {'success': False,"data":{"total":0,"addCount":0}}
            respon_json = tornado.escape.json_encode(respon)
            self.write(respon_json)


class CheckPurchaseInfoHandler(BaseHandler):

    def get(self):
        data = dict()
        orderId = self.get_argument('orderId', '')
        if orderId != '':

            app = ALIBABA()
            d = app.getOrderDetail(orderId)
            result = json.loads(d)

            if result.has_key('result') and result['result']['success']:

                mongo = MongoCase()
                mongo.connect()
                client = mongo.client
                db = client.jingdong

                orderInfo = result['result']['toReturn'][0]

                item = dict()

                if orderInfo.has_key('logistics'):
                    item['logistics'] = orderInfo['logistics']

                if orderInfo.has_key('sellerCompanyName'):
                    item['sellerCompanyName'] = orderInfo['sellerCompanyName']

                if orderInfo.has_key('sellerPhone'):
                    item['sellerPhone'] = orderInfo['sellerPhone']

                if orderInfo.has_key('sellerMobile'):
                    item['sellerMobile'] = orderInfo['sellerMobile']

                item['orderEntries'] = orderInfo['orderEntries']

                try:
                    d = datetime.datetime.strptime(orderInfo['gmtModified'][:14],'%Y%m%d%H%M%S')
                    item['gmtModified'] = d.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass

                try:
                    d = datetime.datetime.strptime(orderInfo['gmtPayment'][:14],'%Y%m%d%H%M%S')
                    item['gmtPayment'] = d.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass


                item['status'] = orderInfo['status']

                item['updateTime'] = datetime.datetime.now()


                db.purchaseList.update({"id": int(orderId)}, {'$set': item})

                data['success'] = True

            else:
                data['success'] = False
                data['msg'] = 'Update ERROR'


        else:
            data['success'] = False
            data['msg'] = 'ERROR'

        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(json.dumps(data, ensure_ascii=False))



class CheckPurchaseLogistHandler(BaseHandler):

    def get(self):
        data = dict()
        ids = self.get_argument('ids', '')
        ids = ids.split(',')
        data['total'] = len(ids)
        data['successCount'] = 0
        data['errorCount'] = 0
        for orderId in ids:

            app = ALIBABA()
            d = app.getOrderDetail(orderId)
            result = json.loads(d)

            if result.has_key('result') and result['result']['success']:

                mongo = MongoCase()
                mongo.connect()
                client = mongo.client
                db = client.jingdong

                orderInfo = result['result']['toReturn'][0]

                item = dict()

                if orderInfo.has_key('logistics'):
                    item['logistics'] = orderInfo['logistics']

                if orderInfo.has_key('sellerCompanyName'):
                    item['sellerCompanyName'] = orderInfo['sellerCompanyName']

                if orderInfo.has_key('sellerPhone'):
                    item['sellerPhone'] = orderInfo['sellerPhone']

                if orderInfo.has_key('sellerMobile'):
                    item['sellerMobile'] = orderInfo['sellerMobile']

                item['orderEntries'] = orderInfo['orderEntries']

                try:
                    d = datetime.datetime.strptime(orderInfo['gmtModified'][:14],'%Y%m%d%H%M%S')
                    item['gmtModified'] = d.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass

                try:
                    d = datetime.datetime.strptime(orderInfo['gmtPayment'][:14],'%Y%m%d%H%M%S')
                    item['gmtPayment'] = d.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass


                item['status'] = orderInfo['status']

                item['updateTime'] = datetime.datetime.now()


                db.purchaseList.update({"id": int(orderId)}, {'$set': item})

                data['successCount'] += 1

            else:
                data['errorCount'] += 1


        respon = data
        respon_json = tornado.escape.json_encode(respon)
        self.write(respon_json)

class MatchPurchaseOrderHandler(BaseHandler):

    def get(self):
        data = dict()
        ids = self.get_argument('ids', '')
        ids = ids.split(',')
        data['total'] = len(ids)
        data['matchCount'] = 0
        mongo = MongoCase()
        mongo.connect()
        client = mongo.client
        db = client.jingdong
        for orderId in ids:

            order = db.orderList.find_one({'order_id':orderId})

            if order and order['order_state'] == 'WAIT_SELLER_STOCK_OUT':

                purchase = db.purchaseList.find({'toFullName':order['consignee_info']['fullname'],'toMobile':order['consignee_info']['mobile'],'createTime':{'$gte':order['createTime']}})


                if order.has_key('matchStatus') and order['matchStatus']>1 :
                    pass
                else:

                    matchItem = []
                    for item in purchase:
                        matchData = dict()
                        matchData['orderId'] = item['id']
                        matchData['orderStatus'] = item['status']
                        if item.has_key('logistics'):
                            matchData['logistics'] = item['logistics']

                        matchItem.append(matchData)


                    if len(matchItem)>0:
                        data['matchCount'] += 1
                        db.orderList.update({'order_id':orderId},{'$set':{'matchItem':matchItem,'matchStatus':1}})



        respon = data
        respon_json = tornado.escape.json_encode(respon)
        self.write(respon_json)

class getPurchaseInfoHandler(BaseHandler):

    def get(self):
        data = dict()
        orderId = self.get_argument('orderId', '')
        if orderId != '':

            mongo = MongoCase()
            mongo.connect()
            client = mongo.client
            db = client.jingdong

            orderInfo = db.purchaseList.find_one({"id": int(orderId)})

            data['data'] = orderInfo
            data['data']['createTime'] = data['data']['createTime'].strftime('%Y-%m-%d %H:%M:%S')
            data['data']['updateTime'] = str(data['data']['updateTime'])
            data['data']['_id'] = str(data['data']['_id'])

            data['success'] = True

        else:
            data['success'] = False
            data['msg'] = 'ERROR'

        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    tornado.options.parse_command_line()
    settings = {
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "xsrf_cookies": True,
        'login_url':'/login'
    }
    app = tornado.web.Application(
        handlers=[(r"/", IndexHandler),
                  (r'/login', LoginHandler),
                  (r'/logout', LogoutHandler),
                  (r"/orderList$", OrderListHandler),
                  (r"/purchaseList$", PurchaseListHandler),
                  (r"/api/checkOrder$", CheckOrderHandler),
                  (r"/api/checkOrderInfo$", ChcekOrderInfoHanlder),
                  (r"/api/getOrderItems$", GetOrderItemsHandler),
                  (r"/api/getSkuImage$", GetSkuImageHandler),
                  (r"/api/checkSku$", CheckSkuHandler),
                  (r"/api/getPurchaseList$", APIGetPurchaseListHandler),
                  (r"/api/getPurchaseInfo$", getPurchaseInfoHandler),
                  (r"/api/checkPurchase$", CheckPurchaseHandler),
                  (r"/api/checkPurchaseInfo$", CheckPurchaseInfoHandler),
                  (r"/api/checkPurchaseLogist$", CheckPurchaseLogistHandler),
                  (r"/api/matchPurchaseOrder$", MatchPurchaseOrderHandler),
                  (r".*", BaseHandler),
                  ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True,
        **settings
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    #http_server.bind(options.port)
    #http_server.start(num_processes=0)
    tornado.ioloop.IOLoop.instance().start()