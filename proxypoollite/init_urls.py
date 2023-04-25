import re

from handle_urls import (process_url_text,
                         process_url_click_1,
                         process_url_json,
                         process_url_json_text,
                         process_url_json_sage,)

# the init_urls is a dict, the key is the url to be crawled, the value is a tuple,
# the first element is a crawl function, the second element is a pattern for generating the next url
# if pattern is none,then no next url, go see further info in crawl function
init_urls = {'http://www.66ip.cn/1.html':
                 (process_url_text, re.compile(r'(?<=cn/)(\d)(?=\.html)')),
             'https://www.89ip.cn/index_1.html':
                 (process_url_text, re.compile(r'(?<=cn/index_)(\d)(?=\.html)')),
             'https://proxy.ip3366.net/free/?action=china&page=1':
                 (process_url_text, re.compile(r'(?<=page\=)(\d)')),
             'https://www.kuaidaili.com/free/inha/1/':
                 (process_url_text, re.compile(r'(?<=inha/)(\d)(?=/)')),
             'https://www.kuaidaili.com/free/intr/1/':
                 (process_url_text, re.compile(r'(?<=/intr/)(\d)(?=/)')),
             'http://www.taiyanghttp.com/free/page1/':
                 (process_url_text, re.compile(r'(?<=/page)(\d)(?=/)')),
             'https://proxy.sage.run/proxy/list?pageNo=1':
                 (process_url_json_sage, re.compile(r'(?<=pageNo\=)(\d)')),
             'https://www.zdaye.com/free/1/?https=1':
                 (process_url_text, re.compile(r'(?<=free/)(\d)(?=/\?https=1)')),
             'http://proxylist.fatezero.org/proxy.list':
                 (process_url_json_text, None),
             'https://proxylist.geonode.com/api/proxy-list?sort_by=lastChecked&sort_type=desc&limit=500':
                 (process_url_json, None),
             'http://www.ip3366.net/free/?stype=1':
                 (process_url_text, None),
             'http://www.ip3366.net/free/?stype=2':
                 (process_url_text, None),
             'http://www.kxdaili.com/dailiip/1/1.html':
                 (process_url_text, re.compile(r'(?<=dailiip/1/)(\d)(?=\.html)')),
             'http://www.kxdaili.com/dailiip/2/1.html':
                 (process_url_text, re.compile(r'(?<=dailiip/2/)(\d)(?=\.html)')),
             'https://www.xsdaili.cn/':
                 (process_url_click_1, re.compile(r'(?<=cn)(/)')),
             }
