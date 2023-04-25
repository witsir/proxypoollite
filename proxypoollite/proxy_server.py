import random
import socketserver
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from handle_log import get_logger
from settings import PROXY_SCORE_MAX, API_PORT, API_HOST, ENABLE_SERVER
from utils import ContextConfig, SingletonMeta

logger = get_logger(__name__)


class WSGIHandler(WSGIRequestHandler):
    def get_environ(self):
        env = super().get_environ()
        env['wsgi.input'] = self.rfile
        env['wsgi.version'] = (1, 0)
        env['wsgi.run_once'] = False
        env['wsgi.multithread'] = True
        env['wsgi.multiprocess'] = False
        return env


class ThreadedWSGIServer(socketserver.ThreadingMixIn, WSGIServer):
    pass


class Server(metaclass=SingletonMeta):

    def __init__(self, ctx_config: ContextConfig, port=API_PORT):
        self.ctx_config = ctx_config
        self.port = port

    def resp_random(self):
        try:
            return random.choice(self.ctx_config.proxy_dict[str(PROXY_SCORE_MAX)])
        except Exception as e:
            logger.warning(e)
            return 'wait'

    def reps_count(self):

        count = sum(len(self.ctx_config.proxy_dict[score]) for score in self.ctx_config.proxy_dict if
                    self.ctx_config.proxy_dict[score])
        return count

    def application(self, environ, start_response):
        path = environ.get('PATH_INFO', '').lstrip('/')
        status = '200 OK'
        if path == '':
            response_body = b'<h2>Welcome to Proxy Pool System</h2>'
        elif path == 'random':
            if random_proxy := self.resp_random():
                response_body = bytes(random_proxy, encoding='utf-8')
            else:
                response_body = b''
        elif path == 'count':
            response_body = bytes(str(self.reps_count()), encoding='utf-8')
        else:
            status = '404 Not Found'
            response_body = b'404 Not Found'

        response_headers = [('Content-Type', 'text/plain'),
                            ('Content-Length', str(len(response_body)))]
        start_response(status, response_headers)
        return [response_body]

    def __call__(self, *args, **kwargs):
        if ENABLE_SERVER:
            server = ThreadedWSGIServer((API_HOST, self.port), WSGIHandler)
            server.set_app(self.application)
            logger.info('server started at http://%s:%s' % ('127.0.0.1', self.port))
            server.serve_forever()
        else:
            logger.info('server not enabled, only can get random proxy from instance in local machine')