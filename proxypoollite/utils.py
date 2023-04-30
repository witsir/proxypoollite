import asyncio
import functools
import itertools
import json
import os.path
import random
import re
import socket
import ssl
import threading
import time
import urllib.request
from functools import wraps
from urllib.error import HTTPError, URLError

from proxypoollite.handle_log import get_logger
from proxypoollite.settings import GET_TIMEOUT, ROOT_DIR, TEST_URL, TEST_VALID_STATUS, PROXY_SCORE_INIT, PROXY_SCORE_MAX, \
    PROXY_SCORE_MIN

logger = get_logger('utils')


class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class ContextConfig(metaclass=SingletonMeta):

    def __init__(self, proxy_dict, lock):
        self.data_dir = None
        self.proxy_data_file = None
        self.proxy_dict = proxy_dict
        self.lock = lock
        self.has_to_json = False

    def to_proxy_dict(self):
        """
        load proxy_dict from json file
        """
        self.data_dir = os.path.join(os.path.dirname(ROOT_DIR), 'data')
        self.proxy_data_file = os.path.join(self.data_dir, 'proxies.json')
        try:
            with open(self.proxy_data_file, 'r') as f:
                dict_copy = json.load(f)
                for key, value in dict_copy.items():
                    self.proxy_dict[key].extend(value)
                logger.info(f'load proxy_dict from {self.proxy_data_file}')
        except Exception as e:
            logger.warning(f'load proxy_dict failed,because {e}')

    def to_json(self):
        """
        dump proxy_dict to json file
        """
        if self.has_to_json:
            logger.info('proxy_dict has already been dumped to json file')
            return
        try:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            with open(self.proxy_data_file, 'w') as f:
                dict_copy = {}
                for key, value in self.proxy_dict.items():
                    dict_copy[key] = list(value)
                json.dump(dict_copy, f)
                self.has_to_json = True
                logger.info(f'dump proxy_dict to {self.proxy_data_file}')
        except Exception as e:
            logger.warning(f'dump proxy_dict failed, because {e}')


def get_domain_from_url(url):
    """
    get domain name from url, domain name then would be used in proxy attribute
    to indicate which website the proxy is from
    """
    pattern = re.compile(r'^(?:https?://)(?:www\.)?([^/]+)(?:\.com|\.cn|\.net|\.org|\.co|\.is|\.run)\D*')
    if domain_name_match := pattern.match(url):
        domain_name = domain_name_match.group(1)
        return domain_name
    else:
        logger.error(f'get domain name failed from {url}')
        return 'NULL'


def retry(max_retries=3, delay=3, is_limit=True):
    """
    retry decorator for fetch_resp
    :param is_limit:
    :param max_retries:
    :param delay:
    :return:
    """

    def decorator(func):
        history = {}

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if is_limit:
                domain = get_domain_from_url(args[0])
                if domain in history and time.time() - history[domain] < 10.1:
                    await asyncio.sleep(10)
                    history[domain] = time.time()
                history[domain] = time.time()
            retries = 0
            while retries < max_retries:
                try:
                    resp = await func(*args, **kwargs)
                    if resp:
                        return resp
                    retries += 1
                    await asyncio.sleep(delay)
                except Exception as e:
                    logger.exception(e)
                    retries += 1
                    await asyncio.sleep(delay)
            return None

        return wrapper

    return decorator


def update_dict(ctx_config: ContextConfig, score, list_):
    """
    update dict with a score
    """
    try:
        ctx_config.proxy_dict[score].extend(list_)
        logger.info(f'update {len(list_)} proxies to {score} in manager.dict')
    except Exception as e:
        logger.exception(f'update dict failed,because {e}')


def add_dict(dict_: dict, score: str, proxy: str):
    """
    update dict with a score
    """
    if score in dict_:
        dict_[score].append(proxy)
    else:
        dict_[score] = [proxy]


_headers = {
    'User-Agent': '',
    'Accept': '*/*',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'utf-8',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
}
ssl._create_default_https_context = ssl._create_unverified_context
_context = ssl.create_default_context()
_context.check_hostname = False
_context.verify_mode = ssl.CERT_NONE


@retry(max_retries=3, delay=5)
async def fetch_resp(url, usr_agent):
    """
    get html entities from url
    :param url: url
    :param usr_agent: user agent
    """
    _headers['User-Agent'] = usr_agent

    try:
        req = urllib.request.Request(url, headers=_headers, method='GET')
        loop = asyncio.get_running_loop()
        get_resp = functools.partial(urllib.request.urlopen, req, context=_context, timeout=GET_TIMEOUT)
        response = await loop.run_in_executor(None, get_resp)
        logger.info(f'get response from {url}')
        resp = response.read().decode('utf-8', errors='ignore')
        return resp
    except (HTTPError, TimeoutError, URLError) as e:
        logger.warning(f'get response from {url} failed, because {e}')
        return None
    except Exception as e:
        logger.exception(f'get response from {url} failed, because {e}')
        return None


async def test_proxy(proxy: (str, str), usr_agent: str, protocol: str = 'https'):
    proxy_ip, proxy_port = proxy
    _headers['User-Agent'] = usr_agent

    handlers = [
        urllib.request.HTTPHandler(),
        urllib.request.HTTPSHandler(context=_context),
        urllib.request.ProxyHandler({protocol: '{}://{}:{}'.format(protocol, proxy_ip, proxy_port)}),
    ]

    socket.setdefaulttimeout(5)
    url = 'https://httpbin.org/ip'
    opener = urllib.request.build_opener(*handlers)
    opener.addheaders = [(k, v) for k, v in _headers.items()]
    loop = asyncio.get_running_loop()
    get_resp = functools.partial(opener.open, url, timeout=GET_TIMEOUT)
    get_resp_test_url = functools.partial(opener.open, TEST_URL, timeout=GET_TIMEOUT)
    try:
        response = await loop.run_in_executor(None, get_resp)
        content = response.read().decode('utf-8')
        origin_ip = json.loads(content)['origin']
        if not origin_ip == proxy_ip:
            return False
        response = await loop.run_in_executor(None, get_resp_test_url)
        logger.info(f'{proxy_ip}:{proxy_port} test with {TEST_URL}  response {response.code}')
        return True if response.code in TEST_VALID_STATUS else False
    except Exception as e:
        logger.warning(f'test proxy {proxy} failed, failed because {e}')
        return False


def _init_scores_list():
    """
    init scores list for tester
    like [10, ..., 1, 50, ..., 41,11, ...,40]
    :return:
    """
    list_ = list(range(PROXY_SCORE_INIT + 1, PROXY_SCORE_MAX - 9))
    random.shuffle(list_)
    int_list = itertools.chain(reversed(range(PROXY_SCORE_MIN + 1, PROXY_SCORE_INIT + 1)),
                               reversed(range(PROXY_SCORE_MAX - 10, PROXY_SCORE_MAX + 1)),
                               list_)
    str_list = [str(i) for i in int_list]
    return str_list


def _get_user_agents():
    with open((os.path.join(os.path.dirname(__file__), 'user_agents.in')), 'r') as f:
        uas = [line.strip() for line in f.readlines()]
    return uas


_user_agents = _get_user_agents()


def get_uer_agent():
    """
    get a random user agent
    """
    return random.choice(_user_agents)


scores_list = _init_scores_list()
