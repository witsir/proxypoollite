import asyncio

from handle_log import get_logger
from scheduler import Scheduler, run_task
import argparse

logger = get_logger('run')
parser = argparse.ArgumentParser(description='ProxyPool')
parser.add_argument('-p', '--processor',
                    type=str,
                    help='processor to run',
                    action='store',
                    choices=['getter', 'tester', 'server'])
args = parser.parse_args()

if __name__ == '__main__':
    sh = Scheduler()
    if args.processor == 'getter':
        try:
            run_task(*sh.getter_task_args)
        except KeyboardInterrupt:
            logger.warning('received keyboard interrupt signal')
    elif args.processor == 'tester':
        try:
            run_task(*sh.tester_task_args)
        except KeyboardInterrupt:
            logger.warning('received keyboard interrupt signal')
        except Exception as e:
            logger.exception(e)
    elif args.processor == 'server':
        try:
            run_task(*sh.server_task_args)
        except KeyboardInterrupt:
            logger.warning('received keyboard interrupt signal')
    else:
        sh.start()
