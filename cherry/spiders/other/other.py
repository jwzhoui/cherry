# -*- coding: utf-8 -*-
# 判断是否为浮点数
import threading
import time
import traceback,sys
# from cherry.spiders.other.jyallLog import mylog
from scrapy.http import HtmlResponse,Request,Response
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

# 失败请求 重新请求一次
def err_request_again(func):
    def call_fun(*args, **kwargs):
        args_ = list(args)+kwargs.values()
        # 线程对象
        response = None
        my_scrapy = None
        request = None
        for a in args_:
            if not response and isinstance(a,Response):
                response = a
            elif not my_scrapy and isinstance(a,scrapy.Spider):
                my_scrapy = a
            elif not request and isinstance(a,Request):
                request = a
            elif response and my_scrapy and request:
                break
        assert response,my_scrapy
        response_code = response.status
        thread = threading.current_thread()
        url = response.url
        thread_err_urls = thread._Thread__kwargs.get('err_url')
        if response_code<200 or response_code>=300:
            # mylog.info('200 url ==%s' % (response.url))
            # 绑定异常url到当前线程
            if thread_err_urls:
                if url in thread_err_urls:
                    thread_err_urls.remove(url)
                    print ('保存url,或抛出异常 已请求过两次, 放弃url==%s' % url)
                    result = func(*args, **kwargs)
                else:
                    thread_err_urls.append(url)
                    # 再次请求
                    if request:
                        print '异常url==%s', url
                        result = request
                    elif response.request:
                        print '异常url==%s', response.url
                        result = response.request
                    else:
                        print ('装饰器使用错误')
            else:
                thread._Thread__kwargs['err_url'] = [url]
                # 再次请求
                result = request
        else:
            thread_err_urls.remove(url) if thread_err_urls and thread_err_urls in thread_err_urls else ''
            result = func(*args, **kwargs)
        return result
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
