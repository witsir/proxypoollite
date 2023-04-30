import asyncio
import json
from pprint import pprint

if __name__ == '__main__':
    # [test processor]
    from proxypoollite.scheduler import Scheduler
    # from proxypoollite.proxy_getter import Getter
    from proxypoollite.proxy_server import Server
    # from proxypoollite.proxy_tester import Tester

    sh = Scheduler()
    # getter = Getter(sh.ctx_config)
    # tester = Tester(sh.ctx_config)
    server = Server(sh.ctx_config)
    print(server.reps_sum())
    # asyncio.run(getter())
    # asyncio.run(tester())

    # [test process_url_text]
    # import asyncio
    # import re
    # asyncio.run(process_url_text('https://www.kuaidaili.com/free/inha/1/', re.compile(r'(?<=inha/)(\d)(?=/)'), sh.ctx_config))

    # [test process_url_click_2]
    # import asyncio
    # import re
    # asyncio.run(process_url_click_2('https://www.zdaye.com/dayProxy.html', re.compile(r'(?<=com)(/dayProxy.html)'), sh.ctx_config))

    # [test fetch_resp for ip info]
    # from proxypoollite.utils import fetch_resp
    # rsp = asyncio.run(fetch_resp('https://api.ipify.org?format=json','Opera/9.63 (X11; Linux x86_64; U; cs) Presto/2.1.1'))
    # pprint(rsp)
    # rsp = asyncio.run(fetch_resp('https://ipapi.com/ip_api.php?ip=222.67.5.191','Opera/9.63 (X11; Linux x86_64; U; cs) Presto/2.1.1'))
    # pprint(json.loads(rsp))
    # rsp = asyncio.run(fetch_resp('http://ipwho.is/','Opera/9.63 (X11; Linux x86_64; U; cs) Presto/2.1.1'))
    # pprint(json.loads(rsp))

    # [test test_proxy]
    # from proxypoollite.utils import test_proxy
    # test_proxy


    # [test init_urls]
    # from proxypoollite.init_urls import init_urls
    # for k, v in init_urls.items():
    #     for i in range(2, 5):
    #         if v[1]:
    #             print(v[1].sub(str(i), k))

    # [test global env variables]
    # from proxypoollite.settings import *
    # for k, v in dict(globals()).items():
    #     if not k.startswith('_') and k.isupper():
    #         print(f'{k}={v}')

    # test wheel
    # from proxypoollite import __main__
    # __main__.main()