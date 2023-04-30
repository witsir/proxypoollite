import os
import platform
import re
from os.path import dirname, abspath, join
import configparser
from logging import Logger

logger = Logger(__name__)

_config_ = configparser.ConfigParser()
_pk_config_path = join(dirname(__file__), '../pk_config.ini')
if os.path.exists(_pk_config_path):
    _config_.read(_pk_config_path)
# definition of flags
IS_WINDOWS = platform.system().lower() == 'windows'

# definition of dirs
ROOT_DIR = dirname(abspath(__file__))
LOG_DIR = join(ROOT_DIR, '../logs')

# definition of environments
DEV_MODE, TEST_MODE, PROD_MODE = 'dev', 'test', 'prod'
# default APP_ENV
APP_ENV = DEV_MODE.lower()

# definition of proxy scores
PROXY_SCORE_MAX = 50
PROXY_SCORE_MIN = 0
PROXY_SCORE_INIT = 10

# definition of proxy number
PROXY_NUMBER_MAX = 3000
PROXY_NUMBER_MIN = 0

# definition of tester cycle, it will test every CYCLE_TESTER second
CYCLE_TESTER = 60 * 5
# definition of getter cycle, it will get proxy every CYCLE_GETTER second
CYCLE_GETTER = 60 * 60 * 2
GET_TIMEOUT = 15

# definition of tester
TEST_URL = 'https://www.weibo.com'
TEST_TIMEOUT = 10
TEST_BATCH = 50

TEST_VALID_STATUS = [200, 206, 302]

# definition of api
API_HOST = '0.0.0.0'
API_PORT = 5555
API_THREADED = True

# flags of enable
ENABLE_TESTER = True
ENABLE_GETTER = True
ENABLE_SERVER = True

# flags of log output files
ENABLE_LOG = True
ENABLE_LOG_CONSOLE = True
ENABLE_LOG_FILE = True
ENABLE_LOG_RUNTIME_FILE = True
ENABLE_LOG_ERROR_FILE = True

_LOG_LEVEL_MAP = {
    DEV_MODE: "DEBUG",
    TEST_MODE: "INFO",
    PROD_MODE: "ERROR"
}


def _merger():
    """
    Merge the dictionary of your machine's environment variables ,
    the default values of the config file which parsed as a dictionary,
    and the dictionary of global variables in the current scope.
    :return:
    """
    # Get the dictionary containing the current scope's global variables which is not starts with '_' and is upper.
    _env_vars = {k: v for k, v in globals().items() if not k.startswith('_') and k.isupper()}
    # Get the dictionary containing the default values of the config file.
    _config_d = {k.upper(): v for k, v in _config_.items('default')}
    for key in _config_d.keys():
        try:
            if type(_env_vars[key]) == bool:
                globals()[key] = bool(_config_.getboolean('default', key))
            elif type(_env_vars[key]) == int:
                globals()[key] = int(_config_d[key])
            elif type(_env_vars[key]) == list:
                if type(_env_vars[key][0]) == int:
                    globals()[key] = [int(i) for i in re.split(r'\s*[;,\s]\s*', _config_d[key])]
                elif type(_env_vars[key][0]) == str:
                    globals()[key] = re.split(r'\s*[;,\s]\s*', _config_d[key])
                elif type(_env_vars[key][0]) == float:
                    globals()[key] = [float(i) for i in re.split(r'\s*[;,\s]\s*', _config_d[key])]
            else:
                globals()[key] = _config_d[key]
        except Exception as e:
            logger.error(f'{e}, {key} parse failed, you should check the the type in a list located in the '
                         f'pk_config.ini file')


if os.path.exists(_pk_config_path):
    _merger()

APP_DEBUG = True if APP_ENV == DEV_MODE else False
APP_DEV = IS_DEV = APP_ENV == DEV_MODE
APP_PROD = IS_PROD = APP_ENV == PROD_MODE
APP_TEST = IS_TEST = APP_ENV == TEST_MODE

# log level
LOG_LEVEL = _LOG_LEVEL_MAP.get(APP_ENV, 'DEBUG')
LOG_ROTATION = True
LOG_RETENTION = True