from scrapy.cmdline import execute

import os
import sys
#
from cherry.spiders.washing.wash import do_washings

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
do_washings()
execute("scrapy crawl beijing_haidian_zufang_1 ".split())


