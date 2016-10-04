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


def snf_index(cls, req):
    """Synnefo-compliant method"""
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'servers_get'
    response = req.get_response(cls.app)
    return cls.get_from_response(response, "servers", [])


OpenStackHelper.index = snf_index


class SNFOCCIMiddleware(OCCIMiddleware):
    """Synnefo wrapper for OCCIMiddleware"""

    def __call__(self, environ, response, *args, **kwargs):
        """Check request for essential AUTH-related headers, early"""

        print environ

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
            user_info = snf_auth.authenticate()
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
