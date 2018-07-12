# -*- coding: utf-8 -*-
import traceback
import urlparse

import scrapy
import time
import sys
from bs4 import BeautifulSoup
from cherry.items import FirstItemLoader, CherryItem
from cherry.spiders.other.jyallLog import mylog
from cherry.spiders.other.other import isNum, get_hous_broker, exec_time, re_request_429
from cherry.spiders.other.redisCache import RedisCache

reload(sys)
sys.setdefaultencoding('utf8')
class DmozSpider(scrapy.Spider):
    name = "beijing_haidian_zufang_1"
    allowed_domains = ['bj.58.com']
    start_urls = [
        'http://bj.58.com/haidian/zufang/1/'
    ]

    def __init__(self):
        self.re_mem = 'http:'
        self.uri = 'bj.58.com'
        self.city = 'bj'

    @re_request_429
    def parse(self, response):
        if response.status != 200:
            print response.statue
        # 区域 # 区域  东城区 昌平区 的链接。。。    response 选择方式：css==XPath==re（正则）
        quyu = response.css(u'dl.secitem:nth-child(1) > dd:nth-child(1) > a:not(:contains("不限"))::attr(href)').extract()
        for q in quyu:
            # mylog.debug('区域url===%s' % (self.re_mem+'//'+self.uri+q))
            yield response.follow(url=self.re_mem+'//'+self.uri+q, callback=self.shangquan)

    @re_request_429
    def shangquan(self, response):
        if response.status != 200:
            print response.statue
        shangquan = response.css('.listUl > li > div:nth-child(1) > a:nth-child(1)::attr(href)').extract()
        for s in shangquan:
            # mylog.debug('url===%s' % (self.re_mem+s))
            yield response.follow(url=self.re_mem+s, callback=self.detail)

    @re_request_429
    def detail(self, response):
        try:
            if response.status != 200:
                print response.statue
            response_url = response.url
            item = FirstItemLoader(item=CherryItem(), response=response)
            item.add_value('source_url', response_url)
            # 标题
            title = response.css('h1.c_333::text').extract_first()
            item.add_value('title',title if title else '')
            # 封面
            image_ = response.css('#smainPic::attr(src)').extract()
            item.add_value('image', self.re_mem+image_[0] if len(image_ )>0 else '')
            # 房屋类型
            # 房屋类型数据
            housing_type= response.css('ul.f14:nth-child(2) > li:nth-child(2) > span:nth-child(2)::text').extract()
            if len(housing_type)>0:
                housing_type_info = housing_type[0]
                # 厅数
                if len(housing_type_info.split('厅'))>1:
                    item.add_value('liveroom_count', housing_type[0].split('厅')[0][-1])
                # 室数
                if len(housing_type_info.split('室')) > 1:
                    item.add_value('bedroom_count', housing_type[0].split('室')[0][-1])
                # 装修名
                housing_type_info_split = housing_type_info.split()
                if housing_type_info_split[-1].__contains__('装修'):
                    item.add_value('renovation_name', housing_type_info_split[-1])
                # 房屋类型名称
                item.add_value('house_type_name', housing_type_info_split[0])
                # 大小
                if len(housing_type_info_split)>1 and isNum(housing_type_info_split[1]):
                    item.add_value('acreage', housing_type_info_split[1])
            # TODO house_type_id   户型id 外键未关联
            # 小区名称
            village_name = response.css('ul.f14:nth-child(2) > li:nth-child(4) > span:nth-child(2) > a:nth-child(1)::text').extract()
            if len(village_name)>0:
                item.add_value('village_name', village_name[0])
            # 来源  爬取
            item.add_value('source_type', '1')
            # 价格
            price = response.css('.f36::text').extract()
            item.add_value('price', price[0] if len(price)>0 else '')
            # 详细地址
            address = response.css('.dz::text').extract()
            item.add_value('address', address[0].replace(' ','').strip() if len(address)>0 else '')
            # 租赁 方式 span.c_333:nth-child(2)
            rental_mode_name = response.css('span.c_333:nth-child(2)::text').extract()
            item.add_value('rental_mode_name', rental_mode_name[0] if len(rental_mode_name)>0 else '')
            # 房屋朝向 u'东南  中层/共32层'
            orientations = response.css('ul.f14:nth-child(2) > li:nth-child(3) > span:nth-child(2)::text').extract()
            if len(orientations)>0 and len(orientations[0].split())>0:
                item.add_value('orientation_name', orientations[0].split()[0])
                # 楼层名称（高中低等）
                floor_names = orientations[0].split()[-1].split('/')
                floor_name = floor_names[0]
                item.add_value('floor_name', floor_name)
            # 房屋描述
            soup = BeautifulSoup(response.text, 'html.parser')
            house_info_ = soup.find_all('span', attrs={'class': 'a2'})
            house_info_ = house_info_[1].get_text() if len(house_info_) > 1 else ''
            item.add_value('house_info', house_info_.replace(' ','').replace('\n',''))
            # 位置 坐标
            coordinates_ = soup.find('a', attrs={
                'onclick': 'clickLog(\'from=fcpc_detail_%s_xiaoquxq_ditu_xiangxi\')' % (self.city)})
            if coordinates_:
                query = urlparse.urlparse(coordinates_.get('href')).query
                parses_coordinates = dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])[
                    'location'].split(',')
                coordinates_lat = parses_coordinates[0]  # 坐标经度
                item.add_value('lat', coordinates_lat)
                coordinates_lng = parses_coordinates[1]  # 坐标纬度
                item.add_value('lng', coordinates_lng)
            # 浏览量
            see_count = response.css('#totalcount::text').extract()
            item.add_value('see_count', see_count[0] if len(see_count)>0 else '')
            # 房源类型 出租房
            item.add_value('house_source_type', '1')
            # 出租房
            item.add_value('second_hand_house', '1')
            item.add_value('update_date', unicode(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            item.add_value('create_date', unicode(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            item.add_value('house_images', [{'source_url':self.re_mem+i,'house_url':response_url} for i in response.css('li[id^=xtu_]::attr(data-src)').extract()])
            # 插入经纪人信息
            broker = {}
            broker_info = response.css('.c_000::text').extract_first()
            if broker_info:
                broker_name_ = broker_info.split('(')
                if len(broker_name_) < 2:
                    print broker_name_
                broker['broker_name'] = broker_name_[0] if len(broker_name_) > 1 else broker_name_
            broker['broker_mobile'] = response.css('.house-chat-txt::text').extract_first()
            broker_company_name = response.css('.agent-subgroup::text').extract_first()
            if broker_company_name:
                broker['broker_company_name'] = broker_company_name.split(' ')[0]
            broker['house_source_url'] = response_url
            # 房源描述
            house_desc_ = soup.find_all('span', attrs={'class': 'a2'})
            broker['house_desc'] = house_desc_[1].get_text().replace(' ', '').replace('\n', '') if len(house_desc_) > 1 else ''
            price = response.css('.f36::text').extract_first()
            broker['price'] = price
            broker['source_type'] = 1
            broker['create_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            broker['last_update_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item.add_value('broker',broker)
            mylog.info('====================================抓取成功===========================================')
            yield item.load_item()
        except Exception, e:
            traceback_template = '''Traceback (most recent call last):
               File "%(filename)s", line %(lineno)s, in %(name)s
             %(type)s: %(message)s\n'''
            traceback.print_exc()
            print (e.message)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = {
                'filename': exc_traceback.tb_frame.f_code.co_filename,
                'lineno': exc_traceback.tb_lineno,
                'name': exc_traceback.tb_frame.f_code.co_name,
                'type': exc_type.__name__,
                'message': exc_value.message,}
            del (exc_type, exc_value, exc_traceback)
            # ## 修改这里就可以把traceback打到任意地方，或者存储到文件中了
            print traceback_template % traceback_details
