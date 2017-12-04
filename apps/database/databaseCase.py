#coding:utf-8

from pymongo import MongoClient
import MySQLdb
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class MongoCase:

    client = None
    db = None

    def connect(self):
        if self.client == None:
            self.client = MongoClient()


class MySQLCase:

    host = '127.0.0.1'
    user = 'root'
    passwd = 'xy2017'
    port = 3306
    charset = 'utf8'
    db = ''

    conn = None


    def __init__(self,db):
        self.db = db

    def connect(self):
        if self.conn == None:
            self.conn=MySQLdb.connect(host=self.host,
                                      user=self.user,
                                      passwd=self.passwd,
                                      db=self.db,
                                      port=self.port,
                                      charset=self.charset)

    def colse(self):
        self.conn.close()
        self.conn = None


    def getData(self,sql):
        if self.conn:
            conn = self.conn
        else:
            self.connect()
            conn = self.conn

        cursor = conn.cursor()

        cursor.execute(sql)
        rawData = cursor.fetchall()

        return rawData


    def getDictData(self,sql):
        if self.conn:
            conn = self.conn
        else:
            self.connect()
            conn = self.conn

        cursor = conn.cursor()

        cursor.execute(sql)
        rawData = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]

        result = []
        for row in rawData:
            objDict = {}
            for index, value in enumerate(row):
                objDict[col_names[index]] = str(value)

            result.append(objDict)

        return result