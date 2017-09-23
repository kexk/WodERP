#coding:utf-8

from pymongo import MongoClient

class MongoCase:

    client = None
    db = None

    def connect(self):
        if self.client == None:
            self.client = MongoClient()