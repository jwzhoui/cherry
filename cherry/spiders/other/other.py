# -*- coding: utf-8 -*-
# 判断是否为浮点数
import threading
import time
import traceback,sys
# from cherry.spiders.other.jyallLog import mylog
from scrapy.http import HtmlResponse,Request
import scrapy
from cherry.spiders.other.redisCache import RedisCache


def isNum(value):
    try:
        float(value) #此处更改想判断的类型
    except TypeError:
        return False
    except ValueError:
        return False
    except Exception as e:
        return False
    else:
        return True

# 插入redis
def insert_redis(*args):
    try:
        table_name = args[1]
        insert_args = args[2]
        RedisCache().set_data(table_name+':2::33::%d' % time.time(), insert_args)
    except Exception,e:
        print e.message


# 函数执行时间
def exec_time(func):
    def call_fun(*args, **kwargs):
        start_time = time.time()
        ss = func(*args, **kwargs)
        end_time = time.time()
        print ('执行 %s 用时：%f秒' % (func.func_name,end_time - start_time))
        return ss
    return call_fun

# 429 重新请求一次
def re_request_429(func):
    def call_fun(*args, **kwargs):
        args_ = list(args)+kwargs.values()
        response = None
        my_scrapy = None
        for a in args_:
            if not response and isinstance(a,HtmlResponse):
                response = a
            elif not my_scrapy and isinstance(a,scrapy.Spider):
                my_scrapy = a
            elif response and my_scrapy:
                break
        assert response,my_scrapy
        response_code = response.status
        if response_code>=200 and response_code<300:
            # mylog.info('200 url ==%s' % (response.url))
            return func(*args, **kwargs)
        else:
            print ('重新请求 %d  url ==%s' % (response_code,response.url))
            threading._sleep(1)
            # 重新请求
            response.follow(url=response.url, callback=func)
    return call_fun


# 插入经纪人
def get_hous_broker(house_url, soup):
    try:
        broker_info = soup.find('div', attrs={'class': 'house-agent-info'})
        broker = {}
        if broker_info:
            broker_name_ = broker_info.select_one('.c_000').get_text().split('(')
            if len(broker_name_) < 2:
                print broker_name_
            broker['broker_name'] = broker_name_[0] if len(broker_name_) > 1 else broker_name_
        broker['broker_mobile'] = soup.select_one('.house-chat-txt').get_text()
        broker['broker_company_name'] = soup.select_one('.agent-subgroup').get_text().split(' ')[0]
        broker['house_source_url'] = house_url
        # 房源描述
        house_desc_ = soup.find_all('span', attrs={'class': 'a2'})
        broker['house_desc'] = house_desc_[1].get_text().replace(' ','').replace('\n','') if len(house_desc_) > 2 else ''
        price_ = soup.find('b', attrs={'class': 'f36'})
        price = price_.get_text() if price_ else ''
        broker['price'] = price
        broker['source_type'] = 1
        broker['create_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        broker['last_update_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return broker
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
        'message': exc_value.message,  }
        del (exc_type, exc_value, exc_traceback)
        # ## 修改这里就可以把traceback打到任意地方，或者存储到文件中了
        print traceback_template % traceback_details
        return broker
