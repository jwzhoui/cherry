# -*- coding: utf-8 -*-
# 判断是否为浮点数
import time
import traceback


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
        broker['house_desc'] = house_desc_[1].get_text() if len(house_desc_) > 2 else ''
        price_ = soup.find('b', attrs={'class': 'f36'})
        price = price_.get_text() if price_ else ''
        broker['price'] = price
        broker['source_type'] = 1
        broker['create_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        broker['last_update_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return broker
    except Exception, e:
        traceback.print_exc()
        print (e.message)
        return broker
