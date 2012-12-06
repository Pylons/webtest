# -*- coding: utf-8 -*-
from waitress.server import WSGIServer
from six.moves import http_client
import threading
import logging
import socket
import webob
import time
import os


def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    ip, port = s.getsockname()
    s.close()
    ip = os.environ.get('WEBTEST_SERVER_BIND', '127.0.0.1')
    return ip, port


class StopableWSGIServer(WSGIServer):

    def __init__(self, application, *args, **kwargs):
        super(StopableWSGIServer, self).__init__(self.wrapper, *args, **kwargs)
        self.main_thread = None
        self.test_app = application
        self.application_url = 'http://%s:%s/' % (self.adj.host, self.adj.port)

    def wrapper(self, environ, start_response):
        if '__file__' in environ['PATH_INFO']:
            req = webob.Request(environ)
            resp = webob.Response()
            resp.content_type = 'text/html; charset=UTF-8'
            filename = req.params.get('__file__')
            body = open(filename, 'rb').read()
            body.replace('http://localhost/',
                         'http://%s/' % req.host)
            resp.body = body
            return resp(environ, start_response)
        elif '__application__' in environ['PATH_INFO']:
            return webob.Response('server started')(environ, start_response)
        return self.test_app(environ, start_response)

    def run(self):
        try:
            self.asyncore.loop(.5, map=self._map)
        except (SystemExit, KeyboardInterrupt):
            self.task_dispatcher.shutdown()

    def shutdown(self):
        # avoid showing traceback related to asyncore
        self.logger.setLevel(logging.FATAL)
        while self._map:
            triggers = list(self._map.values())
            for trigger in triggers:
                trigger.handle_close()
        self.maintenance(0)
        while not self.task_dispatcher.shutdown():
            pass

    @classmethod
    def create(cls, application, **kwargs):
        host, port = _free_port()
        kwargs['port'] = port
        if 'host' not in kwargs:
            kwargs['host'] = host
        server = cls(application, **kwargs)
        thread = threading.Thread(target=server.run)
        server.main_thread = thread
        thread.start()
        return server

    def wait(self):
        conn = http_client.HTTPConnection(self.adj.host, self.adj.port)
        time.sleep(.5)
        for i in range(100):
            try:
                conn.request('GET', '/__application__')
                conn.getresponse()
            except (socket.error, http_client.CannotSendRequest):
                time.sleep(.3)
            else:
                return True
        try:
            self.shutdown()
        except:
            pass
        return False
