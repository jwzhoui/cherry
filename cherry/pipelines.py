# -*- coding: utf-8 -*-


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from cherry.spiders.other.dataBase import SQLiteWraper
from cherry.spiders.other.other import exec_time


class CherryPipeline(object):
    @exec_time
    def process_item(self, item, spider):

        my_dict = dict(item)
        # 数据入库
        db = SQLiteWraper()
        broker = my_dict.pop('broker',{})
        # 插入图片集
        house_images = my_dict.pop('house_images',[])
        for house_image in house_images:
            db.insertData('basic_house_image_info', house_image)
        # 插入经纪人
        db.insertData('broker_house_info', broker)
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
        db.insertData('basic_hous', my_dict)

