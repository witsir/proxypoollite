import asyncio
from asyncio import CancelledError

from proxypoollite.handle_log import get_logger
from proxypoollite.settings import PROXY_SCORE_MAX, PROXY_SCORE_MIN, TEST_BATCH, ENABLE_TESTER
from proxypoollite.utils import ContextConfig, test_proxy, update_dict, add_dict, SingletonMeta, get_uer_agent, scores_list

logger = get_logger('tester')


class Tester(metaclass=SingletonMeta):

    def __init__(self, ctx_config: ContextConfig):
        self.scores_list = scores_list
        self.temp_dict = {}
        self.ctx_config = ctx_config
        self.test_count = 0

    async def test_proxy_in_ctx_dict(self):
        for score in self.scores_list:
            if self.ctx_config.proxy_dict[score]:
                with self.ctx_config.lock:
                    test_list = self.ctx_config.proxy_dict[score][:]
                    self.ctx_config.proxy_dict[score][:] = []
                test_list = set(test_list)
                logger.info(f'start test score: {score} proxies length: {len(test_list)}')
                tasks = [asyncio.create_task(self.is_proxy_anonymous_and_https(score, proxy)) for proxy in test_list]
                await asyncio.gather(*tasks)
                logger.info(f'length {len(test_list)} proxies whose score is {score} has been tested')

                # ↓↓↓↓↓test for split validation, not work well #
                # test_list = list(set(test_list))
                # logger.info(f'start test score: {score} proxies length: {len(test_list)}')
                #
                # batch, rear = divmod(len(test_list), TEST_BATCH)
                # if batch:
                #     for i in range(batch):
                #         tasks = [asyncio.create_task(self.is_proxy_anonymous_and_https(score, proxy)) for proxy in
                #                  test_list[(i * TEST_BATCH):((i+1) * TEST_BATCH)]]
                #         await asyncio.gather(*tasks)
                #         logger.info(f'{batch} of proxies whose score is {score} has been tested')
                # tasks = [asyncio.create_task(self.is_proxy_anonymous_and_https(score, proxy)) for proxy in
                #          test_list[batch * TEST_BATCH:]]
                # await asyncio.gather(*tasks)
                # logger.info(f'{rear} proxies whose score is {score} has been tested')
                # ↑↑↑↑↑ test for split validation, not work well #

    async def is_proxy_anonymous_and_https(self, score, proxy: str):
        """
        test if proxy is anonymous and https supported, and update proxy score in temp_dict
        :param score:
        :param proxy:
        :return:
        """
        proxy_ip, port = proxy.split()[0].split(':')
        is_proxy = await test_proxy((proxy_ip, port), get_uer_agent())
        if is_proxy:
            add_dict(self.temp_dict, str(PROXY_SCORE_MAX), proxy)
            logger.info(f'count:{self.test_count} {proxy} is anonymous and https supported. Score:{PROXY_SCORE_MAX}')
        else:
            if (new_score := int(score) - 1) > PROXY_SCORE_MIN:
                add_dict(self.temp_dict, str(new_score), proxy)
                logger.info(f'count:{self.test_count} {proxy} not anonymous or https not supported. Score: {new_score}')
            else:
                logger.info(f'count:{self.test_count} {proxy} will be deleted. Score:{PROXY_SCORE_MIN}')
        self.test_count += 1
        if self.test_count % TEST_BATCH == 0:
            logger.info(f'{self.test_count // TEST_BATCH} times {TEST_BATCH} of proxies have been tested')
            for score in self.temp_dict:
                update_dict(self.ctx_config, score, self.temp_dict[score])
            self.temp_dict = {}

    async def __call__(self, *args, **kwargs):
        if ENABLE_TESTER:
            try:
                await self.test_proxy_in_ctx_dict()
                for score in self.temp_dict:
                    update_dict(self.ctx_config, score, self.temp_dict[score])
                self.temp_dict = {}
                with self.ctx_config.lock:
                    self.ctx_config.to_json()
            except (CancelledError, KeyboardInterrupt) as e:
                for score in self.temp_dict:
                    update_dict(self.ctx_config, score, self.temp_dict[score])
                self.temp_dict = {}
                with self.ctx_config.lock:
                    self.ctx_config.to_json()
                logger.info('tester is stopped by user')
        else:
            logger.info('tester is disabled')
