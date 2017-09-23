#coding:utf-8


import datetime
import hashlib
import json

import requests


class JDAPI:

    appKey = ''
    apiRoot = ''

    def __init__(self,appKey,apiRoot):

        self.appKey = appKey
        self.apiRoot = apiRoot


    #获取订单列表
    def getOrderList(self,order_state,page_size=100,page=1,option={}):
        method = '360buy.order.search'
        data = {"start_date": "", "end_date": "", "order_state": order_state, "page": page, "page_size": page_size,
         "optional_fields": "", "sortType": "", "dateType": ""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    def getOrderDetail(self,order_id,option={}):
        method = '360buy.order.get'

        data = {"order_state":"","optional_fields":"","order_id":order_id}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    def getOrderDetailV2(self,order_id,optional_fields,order_state=""):
        method = 'jingdong.pop.order.get'

        data = {"order_state":order_state,"optional_fields":optional_fields,"order_id":order_id}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #批量查询未付款订单
    def getNotPayOrderList(self,startDate,endDate,page_size=100,page=1):
        method = 'jingdong.pop.order.notPayOrderInfo'
        data = {"startDate": startDate, "endDate": endDate, "page": page, "page_size": page_size}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #未付款订单单条记录查询
    def getNotPayOrderById(self,orderId):
        method = 'jingdong.pop.order.notPayOrderById'
        data = {"orderId": orderId}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #订单SOP出库:入单个订单id，进行sop出库操作
    def sopOutStorage(self,logistics_id,waybill,order_id,trade_no=""):
        method = '360buy.order.sop.outstorage'
        data = {"logistics_id": logistics_id,"waybill":waybill,"order_id":order_id,"trade_no":trade_no}

        #c = self.getData(method=method, data=data)
        #result = json.loads(c)

        return {"msg":u"暂未开放"}


    #SOP修改运单号:输入单个订单id等修改运单号
    def sopUpdateWaybill(self,order_id,logistics_id,waybill,trade_no=""):
        method = '360buy.order.sop.waybill.update'
        data = {"logistics_id": logistics_id,"waybill":waybill,"order_id":order_id,"trade_no":trade_no}

        #c = self.getData(method=method, data=data)
        #result = json.loads(c)

        return {"msg":u"暂未开放"}


    #查询商家备注
    def getOrderRemark(self,order_id):
        method = 'jingdong.order.venderRemark.queryByOrderId'
        data = {"order_id":order_id}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #商家订单备注修改
    def updateOrderRemark(self,order_id,remark,trade_no="",flag="0"):
        method = '360buy.order.vender.remark.update'
        data = {"order_id":order_id,"remark":remark,"trade_no":trade_no,"flag":flag}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #修改订单收货地址
    def modifyOrderAddress(self,orderId,provinceId,cityId,countyId,option={}):
        method = 'jingdong.pop.order.modifyOrderAddr'
        data = {"orderId":orderId,"provinceId":provinceId,"cityId":cityId,"countyId":countyId,
                "townId":"","detailAddr":"","customerName":"","customerPhone":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #4.获取商家类目信息
    def getSellerCats(self,fields=""):
        method = '360buy.warecats.get'
        data = {"fields": fields}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #5.添加商家商品销售属性
    def addSellerCats(self,category_id,index_id,attribute_id,attribute_value,features,status):
        method = '360buy.wares.vendersellsku.add'
        data = {"category_id": category_id,"index_id":index_id,"attribute_id":attribute_id,
                "attribute_value":attribute_value,"features":features,"status":status}

        #c = self.getData(method=method, data=data)
        #result = json.loads(c)

        return {"msg":u"暂未开放"}


    #6.更新商家商品销售属性
    def updateSellerCats(self,valueId,category_id,index_id,attribute_id,attribute_value,features,status):
        method = '360buy.wares.vendersellsku.update'
        data = {"valueId":valueId,"category_id": category_id,"index_id":index_id,"attribute_id":attribute_id,
                "attribute_value":attribute_value,"features":features,"status":status}

        #c = self.getData(method=method, data=data)
        #result = json.loads(c)

        return {"msg":u"暂未开放"}


    #9.获取单个类目信息
    def categoryFindById(self,cid,option={}):
        method = 'jingdong.category.read.findById'

        data = {"cid":cid,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #10.查找子类目列表
    def findChildCategoryById(self,parentCid,option={}):
        method = 'jingdong.category.read.findByPId'

        data = {"parentCid":parentCid,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #7.获取类目属性列表
    def findAttrsByCategoryId(self,cid,attributeType,option={}):
        method = 'jingdong.category.read.findAttrsByCategoryId'

        data = {"cid":cid,"attributeType":attributeType,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #14.获取类目属性列表
    def findAttrsByCategoryIdJos(self,cid,attributeType,option={}):
        method = 'jingdong.category.read.findAttrsByCategoryIdJos'

        data = {"cid":cid,"attributeType":attributeType,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #2.获取类目属性
    def findAttrById(self,attrId,option={}):
        method = 'jingdong.category.read.findAttrById'

        data = {"attrId":attrId,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #14.获取属性的可选值列表(过滤重复字段名)
    def findAttrByIdJos(self,attrId,option={}):
        method = 'jingdong.category.read.findAttrByIdJos'

        data = {"attrId":attrId,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #3.通过类目属性ID获取属性值列表
    def findValuesByAttrId(self,categoryAttrId,option={}):
        method = 'jingdong.category.read.findValuesByAttrId'

        data = {"categoryAttrId":categoryAttrId,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #15.通过类目属性ID获取属性值列表
    def findValuesByAttrIdJos(self,categoryAttrId,option={}):
        method = 'jingdong.category.read.findValuesByAttrIdJos'

        data = {"categoryAttrId":categoryAttrId,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #8.获取类目属性值
    def findValuesById(self,id,option={}):
        method = 'jingdong.category.read.findValuesById'

        data = {"id":id,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #13.获取类目属性值
    def findValuesByIdJos(self,id,option={}):
        method = 'jingdong.category.read.findValuesByIdJos'

        data = {"id":id,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #11.查询商家已授权的品牌
    def findAuthorizeBrand(self,name=""):
        method = 'jingdong.pop.vender.cener.venderBrand.query'

        data = {"name":name}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #1.获取商家已设置物流公司
    def getLogisticsList(self,optional_fields=""):
        method = '360buy.delivery.logistics.get'
        data = {"optional_fields": optional_fields}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #2.获取商家的所有物流公司
    def getLogisticsCompanyList(self,fields=""):
        method = '360buy.get.vender.all.delivery.company'
        data = {"fields": fields}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #3.添加物流公司
    def addLogisticsCompany(self,delivery_company_id,name,sort,remark):
        method = '360buy.add.vender.delivery.company'
        data = {"delivery_company_id": delivery_company_id,"name":name,"sort":sort,"remark":remark}

        #c = self.getData(method=method, data=data)
        #result = json.loads(c)

        return {"msg":u"暂未开放"}


    #4.删除商家的物流公司
    def deleteLogisticsCompany(self,delivery_company_id):
        method = '360buy.delete.vender.delivery.company'
        data = {"delivery_company_id": delivery_company_id}

        #c = self.getData(method=method, data=data)
        #result = json.loads(c)

        return {"msg":u"暂未开放"}


    #查询图片空间用户信息
    def getUserinfo(self):
        method = 'jingdong.imgzone.userinfo.query'
        data = {}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #查询全量图片
    def getAllImageList(self,category_id="",image_name="",scroll_id=""):
        method = 'jingdong.imgzone.image.queryAll'

        data = {"category_id":category_id,"image_name":image_name,"scroll_id":scroll_id}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #查询图片分类
    def getImageCategory(self,cate_id="",cate_name="",parent_cate_id=""):
        method = 'jingdong.imgzone.category.query'

        data = {"cate_id":cate_id,"cate_name":cate_name,"parent_cate_id":parent_cate_id}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #添加图片分类
    def addImageCategory(self,cate_name="",parent_cate_id=""):
        method = 'jingdong.imgzone.category.add'

        data = {"cate_name":cate_name,"parent_cate_id":parent_cate_id}

        #c = self.getData(method=method, data=data)
        #result = json.loads(c)

        return {"msg":u"暂未开放"}


    #更新分类名称、分类的父分类
    def updateImageCategory(self,cate_id,cate_name="",parent_cate_id=""):
        method = 'jingdong.imgzone.category.update'

        data = {"cate_id":cate_id,"cate_name":cate_name,"parent_cate_id":parent_cate_id}

        #c = self.getData(method=method, data=data)
        #result = json.loads(c)

        return {"msg":u"暂未开放"}


    #查询图片是否被引用
    def isReferenced(self,picture_id):
        method = 'jingdong.imgzone.picture.isreferenced'

        data = {"picture_id":picture_id}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #查询图片列表
    def pictureQuery(self,option={}):
        method = 'jingdong.imgzone.picture.query'

        data = {"picture_id":"","picture_cate_id":"","picture_name":"","start_date":"","end_date":"","page_num":"","page_size":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    def getCarriersList(self):
        method = 'jingdong.logistics.carriers.list'
        data = {}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #获得在京东Alpha平台签约并且状态正常的所有承运商列表
    def getProviderList(self,providerState):
        method = 'jingdong.ldop.alpha.provider.query'
        data = {"providerState":providerState}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #查询运单基本信息接口
    def getWaybillInfo(self,providerCode,waybillCode):
        method = 'jingdong.ldop.alpha.waybill.query'
        data = {"providerCode":providerCode,"waybillCode":waybillCode}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #获取产品列表
    def getProductList(self,option={}):
        method = 'jingdong.ware.read.searchWare4Valid'

        data = {"wareId":"","searchKey":"","searchField":"","categoryId":"","shopCategoryIdLevel1":"",
                "shopCategoryIdLevel2":"","templateId":"","promiseId":"","brandId":"","featureKey":"",
                "featureValue":"","wareStatusValue":"","itemNum":"","barCode":"","colType":"",
                "startCreatedTime":"","endCreatedTime":"","startJdPrice":"","endJdPrice":"",
                "startOnlineTime":"","endOnlineTime":"","startModifiedTime":"","endModifiedTime":"",
                "startOfflineTime":"","endOfflineTime":"","startStockNum":"","endStockNum":"",
                "orderField":"","orderType":"","pageNo":"","pageSize":"","field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #获取单个商品
    def findWareById(self,wareId,option={}):
        method = 'jingdong.ware.read.findWareById'

        data = {"wareId":wareId,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #获取商品或者颜色主图
    def findFirstImage(self,wareId,colorId="0000000000"):
        method = 'jingdong.image.read.findFirstImage'

        data = {"wareId":wareId,"colorId":colorId}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #通过颜色获取商品图片列表
    def findImagesByColor(self,wareId,colorId="0000000000"):
        method = 'jingdong.image.read.findImagesByColor'

        data = {"wareId":wareId,"colorId":colorId}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #获取商品上的所有图片列表
    def findImagesByWareId(self,wareId):
        method = 'jingdong.image.read.findImagesByWareId'

        data = {"wareId":wareId}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #获取单个SKU
    def findSkuById(self,skuId,option={}):
        method = 'jingdong.sku.read.findSkuById'

        data = {"skuId":skuId,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #获取sku库存信息
    def findSkuStock(self,skuId,option={}):
        method = 'jingdong.stock.read.findSkuStock'

        data = {"skuId":skuId,"field":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    # 获取sku库存信息
    def searchSkuList(self, option={}):
        method = 'jingdong.sku.read.searchSkuList'

        data = {"wareId":"","skuId": "","skuStatuValue":"","maxStockNum":"","minStockNum":"","endCreatedTime":"",
                "endModifiedTime":"","startCreatedTime":"","startModifiedTime":"","outId":"","colType":"",
                "itemNum":"","wareTitle":"","orderFiled":"","orderType":"","pageNo":"","page_size":"","field":""}

        for (k, v) in option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #店铺信息查询
    def shopQuery(self):
        method = 'jingdong.vender.shop.query'
        data = {}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    def shipAddressQuery(self):
        method = 'jingdong.vender.shipaddress.query'

        data = {}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    def returnAddressQuery(self):
        method = 'jingdong.vender.returnaddress.query'

        data = {}

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #查询商家基本信息
    def sellerInfoQuery(self,option={}):
        method = 'jingdong.seller.vender.info.get'

        data = {"ext_json_param":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result

    #获取前台展示的商家自定义店内分类
    def sellerCatsQuery(self,option={}):
        method = '360buy.sellercats.get'

        data = {"fields":""}

        for (k,v) in  option.items():
            data[k] = v

        c = requests.post(url=self.apiRoot, data=data)
        result = json.loads(c)

        return result


    #添加卖家自定义店内分类
    def sellerCatsAdd(self,parent_id,name,option={}):
        method = '360buy.sellercat.add'

        data = {"parent_id":parent_id,"name":name,"is_open":"","is_home_show":""}

        for (k,v) in  option.items():
            data[k] = v

        #c = self.getData(method=method, data=data)
        #result = json.loads(c)

        return {"msg":u"暂未开放"}

    #更新商家自定义店内分类
    def sellerCatsUpdate(self,cid,option={}):
        method = '360buy.sellercat.update'

        data = {"cid":cid,"name":"","home_show":""}

        for (k,v) in  option.items():
            data[k] = v

        #c = self.getData(method=method, data=data)
        #result = json.loads(c)

        return {"msg":u"暂未开放"}

    #删除商家自定义店内分类
    def sellerCatsDelete(self,cid):
        method = '360buy.sellercat.delete'

        data = {"cid":cid}

        #c = self.getData(method=method, data=data)
        #result = json.loads(c)

        return {"msg":u"暂未开放"}



