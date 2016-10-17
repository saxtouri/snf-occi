# Copyright (C) 2016 GRNET S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from unittest import TestCase
from mock import patch
from soi import wsgi

environ = {
    'SCRIPT_NAME': '',
    'REQUEST_METHOD': 'GET',
    'PATH_INFO': '/compute',
    'SERVER_PROTOCOL': 'HTTP/1.1',
    'QUERY_STRING': '',
    'CONTENT_LENGTH': '0',
    'HTTP_USER_AGENT': 'curl/7.47.0',
    'SERVER_NAME': '127.0.0.1',
    'REMOTE_ADDR': '127.0.0.1',
    'wsgi.url_scheme': 'http',
    'paste.httpserver.proxy.host': 'dummy',
    'paste.httpserver.proxy.scheme': 'http',
    'SERVER_PORT': '8080',
    'wsgi.input': '<socket._fileobject>',
    'HTTP_HOST': 'localhost:8080',
    'wsgi.multithread': True,
    'HTTP_ACCEPT': '*/*',
    'wsgi.version': (1, 0),
    'wsgi.run_once': False,
    'wsgi.errors': '<stderr>',
    'wsgi.multiprocess': False,
    'CONTENT_TYPE': '',
    'paste.httpserver.thread_pool': 'paste.httpserver.ThreadPool'
}
TOKEN, PROJECT = 'MY-Fake-Token', 'MY-Fake-Project'


def mock_start_response(*args, **kwargs):
    return args, kwargs


class FakeAstakos:
    """A fake kamaki.clients.astakos.AstakosClient"""


class SNFOCCIMiddleware(TestCase):
    """Test SNFOCCIMiddleware wrapper"""

    def setUp(self):
        self.cls = wsgi.SNFOCCIMiddleware
        self.soi = wsgi.SNFOCCIMiddleware(lambda x: x)
        wsgi.mock_start_response = mock_start_response
        self.environ = dict(environ)

    def tearDown(self):
        pass

    @patch('soi.wsgi.mock_start_response')
    def test___call__without_token(self, response):
        """Test SNFOCCIMiddleware without token"""
        r = self.soi(self.environ, response)
        exp = [wsgi.REDIRECT_MSG.format(URL=wsgi.KEYSTONE_URL), ]
        self.assertEquals(r, exp)

        exp_status = '401 Not Authorized'
        exp_headers = [
            ('Content-Type', 'text/html'),
            (
                'Www-Authenticate',
                'Keystone uri=\'{0}\''.format(wsgi.KEYSTONE_URL)
            )
        ]
        response.assert_called_once_with(exp_status, exp_headers)

    @patch('ooi.wsgi.OCCIMiddleware.__call__', return_value='superinstance')
    @patch('soi.wsgi.mock_start_response')
    def test___call__with_headers(self, response, superclass):
        # Test Authentication error
        self.environ['HTTP_X_AUTH_TOKEN'] = TOKEN
        self.environ['HTTP_X_SNF_PROJECT'] = PROJECT
        r = self.soi(self.environ, response)
        self.assertEquals(r, 'superinstance')
        superclass.assert_called_once_with(self.environ, response)
