from scrapy.cmdline import execute

import os
import sys
#
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

execute("scrapy crawl beijing_haidian_zufang_1".split())

