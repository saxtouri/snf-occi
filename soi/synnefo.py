# Copyright 2016 GRNET S.A. All rights reserved. #
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
#   1. Redistributions of source code must retain the above
#      copyright notice, self.list of conditions and the following
#      disclaimer.
#
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, self.list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY GRNET S.A. ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL GRNET S.A OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import json
from kamaki.clients import ClientError
from kamaki.clients.astakos import AstakosClient
from kamaki.clients.cyclades import (
    CycladesComputeClient, CycladesNetworkClient)
from kamaki.clients.utils import https
from soi.config import AUTH_URL, CA_CERTS
import webob.exc

#  endpoints are offered auth-free, so no need for an admin token
ADMIN_TOKEN = ''
https.patch_with_certs(CA_CERTS)
auth = AstakosClient(AUTH_URL, ADMIN_TOKEN)

endpoints = {'identity': AUTH_URL}
client_classes = {'identity': AstakosClient}

for cls in (CycladesComputeClient, CycladesNetworkClient):
    service_type = cls.service_type
    endpoints[service_type] = auth.get_endpoint_url(service_type)
    client_classes[service_type] = cls


def handle_exceptions(f):
    """Run a method, raise Synnefo errors as snf-occi exceptions"""
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ClientError as ce:
            print 'ClientError:', ce, ce.status, ce.details
            exc = {
                400: webob.exc.HTTPBadRequest,
                401: webob.exc.HTTPUnauthorized,
                403: webob.exc.HTTPForbidden,
                404: webob.exc.HTTPNotFound,
                405: webob.exc.HTTPMethodNotAllowed,
                406: webob.exc.HTTPNotAcceptable,
                409: webob.exc.HTTPConflict,
                413: webob.exc.HTTPRequestEntityTooLarge,
                415: webob.exc.HTTPUnsupportedMediaType,
                429: webob.exc.HTTPTooManyRequests,
                501: webob.exc.HTTPNotImplemented,
                503: webob.exc.HTTPServiceUnavailable,
            }.get(ce.status, webob.exc.HTTPInternalServerError)
            raise exc(explanation='{0}'.format(ce.message))
    wrapper.__name__ = f.__name__
    return wrapper


@handle_exceptions
def call_kamaki(environ, start_response, *args, **kwargs):
    """Initialize the requested kamaki client, call the requested method
    :param cls: the kamaki client Class, e.g, CycladesComputeClient
    :param method_name: name of the method to call, e.g. list_servers
    :param args: args for the method method
    :param kwargs: kwargs for the method
    :returns: the response from kamaki, WSGI compliant
    """
    service_type = environ.pop('service_type')
    method_name = environ.pop('method_name')
    kwargs = environ.pop('kwargs', {})
    print '\t', service_type, method_name, kwargs

    if service_type in ('mock', ):
        code, status, headers, body = {
            'empty_list': (200, 'OK', {}, {'empty list': []}),
        }.get(method_name, kwargs.get('req_args', (200, 'OK', {}, None)))

    else:  # Normal case
        endpoint = endpoints[service_type]
        token = environ['HTTP_X_AUTH_TOKEN']
        cls = client_classes[service_type]
        client = cls(endpoint, token)
        method = getattr(client, method_name)

        r = method(*args, **kwargs)
        code, status, headers = r.status_code, r.status, r.headers

        body = None
        if r.content:
            body = _stringify_json_values(r.json)

    bodystr = ''
    if body is not None:
        bodystr = json.dumps(body)
        headers['content-length'] = '{0}'.format(len(bodystr))
        headers.setdefault('content-type', 'application/json')

    start_response('{0} {1}'.format(code, status), headers.items())
    return bodystr


def _stringify_json_values(data):
    """If a sinlge value is not a string, make it"""
    if isinstance(data, dict):
        return dict((k, _stringify_json_values(v)) for k, v in data.items())
    if isinstance(data, list):
        return map(_stringify_json_values, data)
    return '{0}'.format(data) if data else data
