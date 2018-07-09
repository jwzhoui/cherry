# -*- coding: utf-8 -*-
import traceback
import threading
import sqlite3
import MySQLdb
import sys

from cherry import settings

reload(sys)
sys.setdefaultencoding('utf8')
class SQLiteWraper(object):
    """
    数据库的一个小封装，更好的处理多线程写入
    """
    def __init__(self, command='', **kwargs):
        self.lock = threading.RLock()  # 锁
        kwargs = dict(settings.mysql,**kwargs)
        self.host = kwargs.get('host','192.168.3.207')  # 数据库连接参数
        self.port = kwargs.get('port','3306')
        self.user = kwargs.get('user','root')
        self.passwd = kwargs.get('passwd', 'root')
        self.db = kwargs.get('db','bbzf')
        self.charset = kwargs.get('charset','utr8')
        if command != '':
            conn = self.get_conn()
            cu = conn.cursor()
            cu.execute(command)

    def get_conn(self):
        conn = MySQLdb.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.passwd,
            db=self.db,
            charset=self.charset
        )
        return conn

    def conn_close(self, conn=None):
        conn.close()

    def conn_trans(func):
        def connection(self, *args, **kwargs):
            self.lock.acquire()
            conn = self.get_conn()
            kwargs['conn'] = conn
            try:
                rs = func(self, *args, **kwargs)
                return rs
            except Exception ,me:
                print me.message
            finally:
                conn.rollback()
                self.conn_close(conn)
                self.lock.release()

        return connection

    @conn_trans
    def fetchall(self, command="", conn=None):
        cu = conn.cursor()
        lists = []
        try:
            cu.execute(command)
            lists = cu.fetchall()
        except Exception, e:
            print e
            pass
        return lists

    @conn_trans
    def execute(self, command, method_flag=0, conn=None):
        cu = conn.cursor()
        try:
            if not method_flag:
                cu.execute(command)
            else:
                cu.execute(command[0], command[1])
            conn.commit()
        except sqlite3.IntegrityError, e:
            # print e　'insert into xiaoqu values( 东城逸墅,东城,工体,塔板结合, 2009)'
            return -1
        except Exception, e:
            print e
            return -2
        return 0
    def code(self,list):
        for i,s in enumerate(list):
            s = '' if s==None else s
            list[i] = str(s)
        return list
    # 插入数据
    @conn_trans
    def insertData(self, table, my_dict,conn=None):
        try:
            cu = conn.cursor()
            cols = ', '.join(self.code(my_dict.keys()))
            values = ','.join(['"'+str(i)+'"' for i in self.code(my_dict.values())])
            values = values.replace('"null"', 'null').replace('"None"','null').replace('""','null')
            sql = 'insert INTO %s (%s) VALUES (%s)' % (table, cols,  values )
            cu.execute(sql)
            conn.commit()
        except sqlite3.IntegrityError, e:
            traceback.print_exc()
            print e

    # 插入数据 多条
    @conn_trans
    def insertDatas(self, table, items,conn=None):
        try:
            if len(items)<1:
                return
            cu = conn.cursor()
            keys = items[0].keys()
            values = []
            for item in items:
                value = []
                for key in keys:
                    value.append('"'+item[key]+'"')
                value_ = ','.join(value)
                values.append(value_)
            cols = ', '.join(self.code(keys))
            values = ','.join(['('+str(i)+')' for i in self.code(values)])
            values = values.replace('"null"', 'null').replace('"None"','null').replace('""','null')
            sql = 'insert INTO %s (%s) VALUES %s' % (table, cols,  values )
            cu.execute(sql)
            conn.commit()
        except sqlite3.IntegrityError, e:
            traceback.print_exc()
            print e

    @conn_trans
    def get_rental_mode(self, rental_mode_name,conn=None):
        if rental_mode_name is None or rental_mode_name == '':
            return []
        sql = 'select sci.id from sys_code_info sci where sci.name = "%s"' % (rental_mode_name)
        list = conn.fetchall(sql)
        return list

    @conn_trans
    def get_village_info_by_name(self, name,conn=None):
        if name is None or name == '':
            return []
        sql = 'select bvi.id,bvi.name,bvi.city_id,bvi.city_name,bvi.city_pinyin,bvi.area_id,bvi.area_name,bvi.area_pinyin,bvi.trade_area_id,bvi.trade_area_name' \
              ',bvi.metro_id,bvi.metro_name,bvi.station_id,bvi.station_name,bvi.address,bvi.province_id,bvi.province_name,bvi.province_pinyin from basic_village_info bvi where bvi.name = "%s"' % (
              name)
        list = conn.fetchall(sql)
        return list
