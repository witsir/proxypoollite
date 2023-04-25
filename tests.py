import asyncio
import json
import multiprocessing
import queue
import re
from pprint import pprint
from threading import Thread

from proxypoollite.init_urls import init_urls
from proxypoollite.proxy_getter import Getter
from proxypoollite.proxy_server import Server
from proxypoollite.proxy_tester import Tester
from proxypoollite.scheduler import Scheduler
from proxypoollite.utils import fetch_resp

if __name__ == '__main__':
    sh = Scheduler()
    getter = Getter(sh.ctx_config)
    tester = Tester(sh.ctx_config)
    server = Server(sh.ctx_config)
    print(server.reps_count())
    # asyncio.run(getter())
    # asyncio.run(tester())
    # asyncio.run(process_url_text('https://www.kuaidaili.com/free/inha/1/', re.compile(r'(?<=inha/)(\d)(?=/)'), sh.ctx_config))
    # asyncio.run(process_url_click_2('https://www.zdaye.com/dayProxy.html', re.compile(r'(?<=com)(/dayProxy.html)'), sh.ctx_config))
    # for k, v in init_urls.items():
    #     for i in range(2, 5):
    #         if v[1]:
    #             print(v[1].sub(str(i), k))
    # pprint(json.loads(rsp)['headers'])