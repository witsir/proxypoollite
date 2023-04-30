import argparse
"""
support run 'python3 proxypoollite' in command line, and 'python3 -m proxypoollite' still works
not recommended, I've pre-disabled this feature.
recommended way is to go to project and 'pip install -e .' Then you can run one of the followings in command line:
python3 -m proxypoollite
python3 proxypoollite
proxypoollite
"""
# import sys
# from os.path import abspath, dirname
# sys.path.append(dirname(dirname(abspath(__file__))))

from proxypoollite import settings

from proxypoollite.handle_log import get_logger
from proxypoollite.scheduler import Scheduler, run_task

logger = get_logger('run')
parser = argparse.ArgumentParser(description='ProxyPool')
parser.add_argument('-p', '--processor',
                    type=str,
                    help='processor to run',
                    action='store',
                    choices=['getter', 'tester', 'server'])
parser.add_argument('-dev', '--development',
                    help='development mode',
                    action='store_true')

args = parser.parse_args()


def change_dev():
    """
    change to development mode
    """
    settings.APP_ENV = 'dev'
    settings.APP_DEBUG = True
    settings.APP_DEV = settings.IS_DEV = True
    settings.APP_PROD = settings.IS_PROD = False
    settings.APP_TEST = settings.IS_TEST = False
    settings.LOG_LEVEL = "DEBUG"


def main():
    if args.development:
        change_dev()
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


if __name__ == '__main__':
    main()
