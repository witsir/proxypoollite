import asyncio
import multiprocessing
import time

from proxypoollite.handle_log import get_logger
from proxypoollite.proxy_getter import Getter
from proxypoollite.proxy_server import Server
from proxypoollite.proxy_tester import Tester
from proxypoollite.settings import CYCLE_GETTER, CYCLE_TESTER, ENABLE_SERVER, ENABLE_GETTER, ENABLE_TESTER, IS_WINDOWS
from proxypoollite.utils import ContextConfig, scores_list

logger = get_logger('Scheduler')

if IS_WINDOWS:
    multiprocessing.freeze_support()


def run_task(job, is_enable, cycle):
    """
    run tester
    """
    if not is_enable:
        logger.warning(f'{job.__class__.__name__} not enabled, exit')
        return
    if job.__class__.__name__ == 'Server':
        job()
    else:
        loop = 0
        while True:
            logger.debug(f'{job.__class__.__name__} loop {loop} start...')
            asyncio.run(job())
            loop += 1
            time.sleep(cycle)


class Scheduler:
    def __init__(self):
        self.manager = multiprocessing.Manager()
        self.proxy_dict = self.init_proxy_dict()
        self.lock = self.manager.Lock()
        self.ctx_config = self.init_ctx_config()
        self.getter_task_args = (Getter(self.ctx_config), ENABLE_GETTER, CYCLE_GETTER)
        self.tester_task_args = (Tester(self.ctx_config), ENABLE_TESTER, CYCLE_TESTER)
        self.server_task_args = (Server(self.ctx_config), ENABLE_SERVER, True)

    def init_proxy_dict(self):
        """
        init proxy dict
        """
        proxy_dict = self.manager.dict()
        for score in scores_list:
            proxy_dict[score] = self.manager.list()
        return proxy_dict

    def init_ctx_config(self):
        """
        init ctx config
        """
        ctx_config = ContextConfig(self.proxy_dict, self.lock)
        ctx_config.to_proxy_dict()
        return ctx_config

    def start(self):
        processes = []
        p_getter, p_tester, p_server = None, None, None
        try:
            logger.info('starting proxypoollite...')
            p_getter = multiprocessing.Process(target=run_task, args=self.getter_task_args)
            p_tester = multiprocessing.Process(target=run_task, args=self.tester_task_args)
            p_server = multiprocessing.Process(target=run_task, args=self.server_task_args)
            p_getter.start()
            processes.append(p_getter)
            logger.info(f'starting getter, pid {p_getter.pid}...')
            p_tester.start()
            processes.append(p_tester)
            logger.info(f'starting tester, pid {p_tester.pid}...')
            p_server.start()
            processes.append(p_server)
            logger.info(f'starting server, pid {p_server.pid}...')
            _ = [p.join() for p in processes]
        except KeyboardInterrupt as e:
            logger.info(f'received keyboard interrupt signal {e}')
            self.ctx_config.to_json()
            _ = [p.terminate() for p in processes]
        except Exception as e:
            logger.exception(e)
            self.ctx_config.to_json()
            self.manager.shutdown()
        finally:
            # must call join method before calling is_alive
            _ = [p.join() for p in processes]
            logger.info(f'getter is {"alive" if p_getter.is_alive() else "dead"}')
            logger.info(f'tester is {"alive" if p_tester.is_alive() else "dead"}')
            logger.info(f'server is {"alive" if p_server.is_alive() else "dead"}')
            logger.info('proxy terminated')
            self.manager.shutdown()