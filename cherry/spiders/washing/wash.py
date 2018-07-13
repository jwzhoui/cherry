# -*- coding: utf-8 -*-


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import threading

from cherry.spiders.other.dataBase import SQLiteWraper
from cherry.spiders.other.other import exec_time
from cherry.spiders.other.redisCache import connection
from multiprocessing import freeze_support,Pool,RLock
import json
from cherry import settings
import time

def washing_images(a=None,b=None,c=None):

    while True:
        # time.sleep(0.14)
        # print time.time()
        # 房屋图片信息
        r_basic_house_image_info = connection.rpop(settings.R_L_BASIC_HOUSE_IMAGE_INFO)
        if not r_basic_house_image_info:
            r_basic_house_image_info = '{}'
            time.sleep(0.1)
        basic_house_image_info = json.loads(r_basic_house_image_info)
        print a,b,c
        print 22

def washing_house(a=None,b=None,c=None):

    while True:
        # time.sleep(0.14)
        # print time.time()

        # 房屋详情信息
        r_basic_hous_info = connection.rpop(settings.R_L_BASIC_HOUS_INFO)
        if not r_basic_hous_info:
            r_basic_hous_info = '{}'
            time.sleep(0.011)
        basic_hous_info = json.loads(r_basic_hous_info)
        print a,b,c
        print 33

def washing_broker(a=None,b=None,c=None):

    while True:
        # time.sleep(0.14)
        # print time.time()
        # 房屋图片信息
        # 房屋经纪人信息
        r_broker_house_info = connection.rpop(settings.R_L_BROKER_HOUSE_INFO)
        if not r_broker_house_info:
            r_broker_house_info = '{}'
            time.sleep(0.01)
        broker_house_info = json.loads(r_broker_house_info)
        print 11
        print a,b,c

def qwe(**kwargs):
    while True:
        time.sleep(1)
        print time.time()

def do_washings():
    global lock
    lock = RLock()

    freeze_support()
    pool = Pool(3) #线程池中的同时执行的进程数为6
    # for i in range(1):
    pool.apply_async(func=washing_broker,args=(),kwds={'a':'a'}) #线程池中的同时执行的进程数为3，当一个进程执行完毕后，如果还有新进程等待执行，则会将其添加进去
    pool.apply_async(func=washing_house,args=(),kwds={'b':'b'}) #线程池中的同时执行的进程数为3，当一个进程执行完毕后，如果还有新进程等待执行，则会将其添加进去
    pool.apply_async(func=washing_images,args=(),kwds={'c':'c'}) #线程池中的同时执行的进程数为3，当一个进程执行完毕后，如果还有新进程等待执行，则会将其添加进去
        # pool.apply(func=Foo,args=(i,))

    print('end')
    pool.close()
    # pool.join()#调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束

class CherryPipeline(object):
    @exec_time
    def process_item(self, item, spider):
        redis_connection = connection

        my_dict = dict(item)
        # 数据入库
        db = SQLiteWraper()
        broker = my_dict.pop('broker',{})
        # 插入图片集
        house_images = my_dict.pop('house_images',[])
        for house_image in house_images:
            redis_connection.lpush('bbzf:crawl:'+'basic_house_image_info', house_image)
            # db.insertData('basic_house_image_info', house_image)
        # 插入经纪人
        redis_connection.lpush('bbzf:crawl:' + 'broker_house_info', broker)
        # db.insertData('broker_house_info', broker)
        #出租方式id
        rental_mode_ids = db.get_rental_mode(my_dict.get('rental_mode_name',None))
        if rental_mode_ids is not None and len(rental_mode_ids) > 0:
            rental_mode_id = rental_mode_ids[0][0]
            my_dict['rental_mode_id'] = rental_mode_id
        # 小区关联信息
        village_infos = db.get_village_info_by_name(my_dict.get('village_name',None))
        if village_infos and len(village_infos) > 0:
            village_info = village_infos[0]
            my_dict['village_id'] = village_info[0]
            my_dict['village_name'] = village_info[1]
            my_dict['city_id'] = village_info[2]
            my_dict['city_name'] = village_info[3]
            my_dict['city_pinyin'] = village_info[4]
            my_dict['area_id'] = village_info[5]
            my_dict['area_name'] = village_info[6]
            my_dict['area_pinyin'] = village_info[7]
            my_dict['trade_area_id'] = village_info[8]
            my_dict['trade_area_name'] = village_info[9]
            my_dict['metro_id'] = village_info[10]
            my_dict['metro_name'] = village_info[11]
            my_dict['metro_station_id'] = village_info[12]
            my_dict['metro_station_name'] = village_info[13]
            my_dict['address'] = village_info[14]
            my_dict['province_id'] = village_info[15]
            my_dict['province_name'] = village_info[16]
            my_dict['province_pinyin'] = village_info[17]
        # 房屋详情
        redis_connection.lpush('bbzf:crawl:' + 'basic_hous', my_dict)
        # db.insertData('basic_hous', my_dict)

# washing()
do_washings()
print 123