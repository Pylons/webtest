# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__doc__ = '''Allow to run an external process to test your application'''
from webtest import app as testapp
from webtest.http import StopableWSGIServer
from contextlib import contextmanager
from six import binary_type
import subprocess
import logging
import tempfile
import shutil
import time
import sys
import re
import os

log = logging.getLogger('nose.casperjs')
stderr = sys.stderr


class TestApp(testapp.TestApp):
    """Run the test application in a separate thread to allow to access it via
    http"""

    def __init__(self, app=None, url=None, timeout=30000,
                 extra_environ=None, relative_to=None, **kwargs):
        super(TestApp, self).__init__(app, relative_to=relative_to)
        self.server = StopableWSGIServer.create(app)
        self.server.wait()
        self.application_url = self.server.application_url
        os.environ['APPLICATION_URL'] = self.application_url
        self.extra_environ = extra_environ or {}
        self.timeout = timeout
        self.test_app = self

    def get_binary(self, name):
        for path in (os.getcwd(), '/usr/local', '/usr', '/opt'):
            filename = os.path.join(path, 'bin', name)
            if os.path.isfile(filename):
                return filename

    def close(self):
        """Close WSGI server if needed"""
        if self.server:
            self.server.shutdown()

_re_result = re.compile(
   r'.*([0-9]+ tests executed in [0-9\.]+s, [0-9]+ passed, ([0-9]+) failed).*')


@contextmanager
def casperjs(test_app, timeout=60):
    """A context manager to run a test with a :class:`webtest.ext.TestApp`"""
    app = TestApp(test_app.app)
    binary = app.get_binary('casperjs')
    tempdir = tempfile.mkdtemp(prefix='casperjs')

    def run(script, *args):
        dirname = os.path.dirname(sys._getframe(1).f_code.co_filename)
        log = os.path.join(tempdir, os.path.basename(script) + '.log')
        script = os.path.join(dirname, script)
        if binary:
            stdout = open(log, 'ab+')
            cmd = [binary, 'test'] + list(args) + [script]
            p = subprocess.Popen(cmd,
                    stdout=stdout,
                    stderr=subprocess.PIPE)
            end = time.time() + timeout
            while time.time() < end:
                ret = p.poll()
                if ret is not None:
                    end = time.time() + 100
                    break
                time.sleep(.3)
            if time.time() < end:
                try:
                    p.kill()
                except OSError:
                    pass

            if os.path.isfile(log):
                with open(log) as fd:
                    output = fd.read()

            if isinstance(output, binary_type):
                output = output.decode('utf8', 'replace')

            fail = True
            match = _re_result.match(output.replace('\n', ' '))
            if match is not None:
                text, failed = match.groups()
                if int(failed):
                    fail = True
                else:
                    fail = False
                    stderr.write(text + ' ')

            if fail:
                print(output)
                raise AssertionError(
                    'Failure while running %s' % ' '.join(cmd))

    try:
        yield run
    finally:
        shutil.rmtree(tempdir)
        app.close()
