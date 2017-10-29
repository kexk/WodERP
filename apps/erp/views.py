#coding:utf-8


from base import BaseHandler

import hashlib
import datetime
import os.path
import uuid
import tornado.web
from apps.database.databaseCase import *
from bson import ObjectId


class SKUListHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):

        AUTHOR_MOUDLE = 'ViewSKUList'

        user = self.current_user
        role = self.get_secure_cookie("role") if self.get_secure_cookie("role") else 'None'
        

        mongo = MongoCase()
        mongo.connect()
        client = mongo.client

        db = client.woderp

        account = db.user.find_one({'account':user})

        authority = self.getAuthority(account,AUTHOR_MOUDLE)

        if authority['Allow']:

            status = self.get_argument('status','onSelling')
            store = self.get_argument('store','')
            wd = self.get_argument('wd','')
            sort = self.get_argument('sort','gmtModified')
            create = self.get_argument('create','')
            page = self.get_argument('page','1')
            pageSize = self.get_argument('pageSize','200')


            try:
                page = int(page)
            except:
                page = 1

            try:
                pageSize = int(pageSize)
            except:
                pageSize = 1


            erp = MySQLCase('erp_online')
            erp.connect()

            sql = 'select id,`status`,cateId,tagId,skuNameCN,skuNameEN,productId,sku,storage_num,imageURL,CREATE_DATE,' \
                  ' weight,weight0,weight1,buyCount,realStock,attributes,lockCount,warehouseCount,' \
                  'buyLink,addPrice,skuPrice from sys_product_sku '
            sql0 = 'select count(*) as count from sys_product_sku '

            filterStr = 'where inUse=1 '

            sql += filterStr
            sql0 += filterStr

            sql += ' limit %d,%d'%((page-1)*pageSize,pageSize)

            productData = erp.getDictData(sql)

            foo = erp.getDictData(sql0)

            erp.colse()

            totalCount = int(foo[0]['count'])

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
            filterData['statusList'] = []
            filterData['appList'] = []
            filterData['sort'] = sort
            filterData['create'] = create

            self.render('erp/sku-list.html',productData = productData,pageInfo = pageInfo,filterData=filterData,userInfo={'account':user,'role':role})

            #self.render('index.html')

        else:
            #self.write("No Permission")
            self.render('error/message.html', msg={'Msg': 'No Permission', 'Code': 400,'Title':'无权限！','Link':'/'})

