import asyncio
from asyncio import CancelledError

from handle_log import get_logger
from init_urls import init_urls
from settings import ENABLE_GETTER
from utils import ContextConfig, SingletonMeta

logger = get_logger('getter')


class Getter(metaclass=SingletonMeta):

    def __init__(self, ctx_config: ContextConfig):
        self.ctx_config = ctx_config
        self.initial_urls = init_urls

    async def process_init_urls(self):
        """
        build some Thread pools for processing initial urls
        """
        tasks = [asyncio.create_task(func(url, pattern, self.ctx_config)) for url, (func, pattern) in
                 self.initial_urls.items()]
        logger.info('all initial urls start processing')
        await asyncio.gather(*tasks)

    async def __call__(self, *args, **kwargs):
        if ENABLE_GETTER:
            try:
                await self.process_init_urls()
                self.ctx_config.to_json()
                logger.info('all initial urls have been processed')
            except (CancelledError, KeyboardInterrupt) as e:
                with self.ctx_config.lock:
                    self.ctx_config.to_json()
                logger.warning(f'getter is interrupted {e}')
        else:
            logger.info('getter is disabled')
