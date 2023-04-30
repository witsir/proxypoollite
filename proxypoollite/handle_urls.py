import asyncio
import json
import re
from pprint import pprint

from handle_log import get_logger, LOG_FORMAT_LITE
from utils import fetch_resp, update_dict, ContextConfig, get_domain_from_url, get_uer_agent

logger = get_logger('getter')
logger_lite = get_logger('getter', LOG_FORMAT_LITE)


async def _get_url_then_proxies_from_url(url, pattern, ctx_config: ContextConfig):
    """
    handle url to get next urls and then get more proxies from next urls
    """
    new_urls = [pattern.sub(str(i), url) for i in range(2, 5)]
    lst_str = '\n'.join(new_urls)
    logger_lite.info(f'New urls to fetch\n{lst_str}')
    tasks = [asyncio.create_task(process_url_text(new_url, None, ctx_config)) for new_url in new_urls]
    await asyncio.gather(*tasks)


async def _get_url_then_proxies_from_click_url(url, suffix_urls, pattern, ctx_config):
    """
    handle url to get next urls and then get more proxies from next urls
    for https://www.xsdaili.cn/
    """
    new_urls = [pattern.sub(suffix_url, url) for suffix_url in suffix_urls]
    lst_str = '\n'.join(new_urls)
    logger_lite.info(f'New urls to fetch\n{lst_str}')
    tasks = [asyncio.create_task(process_url_text(new_url, None, ctx_config)) for new_url in new_urls]
    await asyncio.gather(*tasks)


def get_proxies_from_html(url, html, ctx_config: ContextConfig):
    """
    get list of proxies from html
    """
    domain_name = get_domain_from_url(url)
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\D+(\d{1,5})')
    lst = pattern.findall(html)
    lst = [f'{item[0]}:{item[1]} {domain_name}' for item in lst]
    lst_str = '\n'.join(lst)
    update_dict(ctx_config, "10", lst)
    logger_lite.info(f'get {len(lst)} new proxies from {url}\n {lst_str}')


def get_proxies_from_json(url, json_data, ctx_config: ContextConfig):
    """
    get list of proxies from json
    """
    domain_name = get_domain_from_url(url)
    try:
        dict_data = json.loads(json_data)
        key = list(dict_data.keys())[0]
        list_data = dict_data[key]
        lst = [f"{item['ip']}:{item['port']} {domain_name}" for item in list_data]
        lst_str = '\n'.join(lst)
        update_dict(ctx_config, "10", lst)
        logger_lite.info(f'get {len(lst)} new proxies from {url}\n {lst_str}')
    except Exception as e:
        logger.exception(f'get proxies from {url} failed, the error is {e}')


def get_proxies_from_json_sage(url, json_data, ctx_config: ContextConfig):
    """
    get list of proxies from json(sage)
    """
    domain_name = get_domain_from_url(url)
    try:
        dict_data = json.loads(json_data)
        list_data = dict_data['data']['list']
        lst = [f"{item['ip']}:{item['port']} {domain_name}" for item in list_data]
        lst_str = '\n'.join(lst)
        update_dict(ctx_config, "10", lst)
        logger_lite.info(f'get {len(lst)} new proxies from {url}\n {lst_str}')
    except Exception as e:
        logger.exception(e)


def get_proxies_from_json_text(url, content, ctx_config: ContextConfig):
    """
        get list of proxies from json
        """
    domain_name = get_domain_from_url(url)
    try:
        lines = content.strip().split('\n')
        lst = [json.loads(line) for line in lines]
        lst = [f"{item['host']}:{item['port']} {domain_name}" for item in lst]
        lst_str = '\n'.join(lst)
        logger_lite.info(f'get {len(lst)} new proxies from {url}\n {lst_str}')
        update_dict(ctx_config, "10", lst)
    except Exception as e:
        logger.exception(e)


async def process_url_text(url, pattern, ctx_config: ContextConfig):
    """
    process url whose response type is text, and it contains next pages and proxies for next crawling
    :param pattern:
    :param url:
    :param ctx_config:
    :return:
    """
    logger.info(f'process url {url}')
    content = await fetch_resp(url, get_uer_agent())
    if content:
        get_proxies_from_html(url, content, ctx_config)
    if pattern:
        await _get_url_then_proxies_from_url(url, pattern, ctx_config)


async def process_url_json_text(url, _, ctx_config: ContextConfig):
    """
    process url whose response is 'json' one line
    :param _:
    :param ctx_config:
    :param url:
    :return:
    """
    logger.info(f'process url {url}')
    content = await fetch_resp(url, get_uer_agent())
    if content:
        get_proxies_from_json_text(url, content, ctx_config)


async def process_url_json(url, _, ctx_config: ContextConfig):
    """
    process url whose response is 'json'
    :param ctx_config:
    :param url:
    :param _:
    :return:
    """
    logger.info(f'process url {url}')
    content = await fetch_resp(url, get_uer_agent())
    if content:
        get_proxies_from_json(url, content, ctx_config)


async def process_url_json_sage(url, _, ctx_config: ContextConfig):
    """
    process url whose response is 'json'
    :param ctx_config:
    :param url:
    :param _:
    :return:
    """
    logger.info(f'process url {url}')
    content = await fetch_resp(url, get_uer_agent())
    if content:
        get_proxies_from_json_sage(url, content, ctx_config)


async def process_url_click_1(url, pattern, ctx_config: ContextConfig):
    """
    special method for day update type url
    :param pattern:
    :param ctx_config:
    :param url:
    :return:
    """
    logger.info(f'process url {url}')
    content = await fetch_resp(url, get_uer_agent())
    if content:
        try:
            suffix_urls = re.findall(r'(?<=href=\")(/dayProxy/ip/\d{4}\.html)(?=\"[\D,\s]*?阅读全文)', content)[:4]
            await _get_url_then_proxies_from_click_url(url, suffix_urls, pattern, ctx_config)
        except Exception as e:
            logger.exception(f'should get urls and proxies in {url}, but some errors happen. {e}')
