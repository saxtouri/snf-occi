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

from ooi.wsgi import OCCIMiddleware
from ooi.api.helpers import OpenStackHelper
from soi.config import KEYSTONE_URL
from soi.synnefo import AstakosClient, AUTH_URL
from kamaki.clients import ClientError


def snf_index(cls, req):
    """Synnefo: list servers"""
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'servers_get'
    response = req.get_response(cls.app)
    return cls.get_from_response(response, "servers", [])


def snf_get_flavors(cls, req):
    """Synnefo: list flavors"""
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'flavors_get'
    req.environ['kwargs'] = {'detail': True}
    response = req.get_response(cls.app)
    return cls.get_from_response(response, 'flavors', [])


def snf_get_images(cls, req):
    """Synnefo: list images"""
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'images_get'
    req.environ['kwargs'] = {'detail': True}
    response = req.get_response(cls.app)
    return cls.get_from_response(response, 'images', [])


def snf_empty_list_200(cls, req):
    """return OK 200 and empty list"""
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'servers_get'
    response = req.get_response(cls.app)
    return cls.get_from_response(response, 'return_empty_list', [])


OpenStackHelper.index = snf_index
OpenStackHelper.get_flavors = snf_get_flavors
OpenStackHelper.get_images = snf_get_images
OpenStackHelper.get_floating_ip_pools = snf_empty_list_200


class SNFOCCIMiddleware(OCCIMiddleware):
    """Synnefo wrapper for OCCIMiddleware"""

    def __call__(self, environ, response, *args, **kwargs):
        """Check request for essential AUTH-related headers, early"""
        if 'HTTP_X_AUTH_TOKEN' not in environ:
            print "No token provided, redirect to Astavoms"
            status = '401 Not Authorized'
            headers = [
                ('Content-Type', 'text/html'),
                (
                    'Www-Authenticate',
                    'Keystone uri=\'{0}\''.format(KEYSTONE_URL))
            ]
            response(status, headers)
            print '401 - redirect to: {0}'.format(KEYSTONE_URL)
            return [str(response)]

        print 'Token provided'
        snf_token = environ['HTTP_X_AUTH_TOKEN']

        try:
            snf_project = environ.get(
                'HTTP_X_SNF_PROJECT', environ['HTTP_X_PROJECT_ID'])
            print 'Project ID provided'
        except KeyError:
            print "No project header, ask Astakos for project ID"
            snf_auth = AstakosClient(AUTH_URL, snf_token)

            try:
                user_info = snf_auth.authenticate()
            except ClientError as ce:
                print ce.status, ce, ce.details
                status = '{0} {1}'.format(ce.status, ce)
                headers = [
                    ('Content-Type', 'application/json'),
                    ('Content-Length', len(ce.details))
                ]
                response(status, headers)
                return [ce.details, ]

            projects = user_info['access']['user']['projects']
            user_uuid = user_info['access']['user']['id']
            snf_project = user_uuid
            for project in projects:
                if project != user_uuid:
                    snf_project = project
                    print "Found a project - hope it suffices"
                    break
            if snf_project == user_uuid:
                print 'Fall back to user UUID as project ID'
        environ['HTTP_X_PROJECT_ID'] = snf_project

        return super(SNFOCCIMiddleware, self).__call__(
            environ, response, *args, **kwargs)
