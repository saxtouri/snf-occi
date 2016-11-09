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
from soi.config import VOLUME_TYPE


def _openstackify_volumes_display_names(response):
    """Add a key called 'displayName'(this is used by OpenStack) and
    place the value of Synnefo's response key (display_name)"""

    for volume_info in response:
        volume_info['displayName'] = volume_info['display_name']


def snf_get_volumes(cls, req):
    """Synnefo: list volumes"""
    req.environ['service_type'] = 'volume'
    req.environ['method_name'] = 'volumes_get'
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "volumes", [])
    _openstackify_volumes_display_names(r)
    return r


def _openstackify_volume_display_name(response):
    """Add a key called 'displayName'(this is used by OpenStack) and
    place the value of Synnefo's response key (display_name)"""

    response['displayName'] = response['display_name']


def snf_get_volume_info(cls, req, volume_id):
    """Synnefo: Get volume info"""
    req.environ['service_type'] = 'volume'
    req.environ['method_name'] = 'volumes_get'
    req.environ['kwargs'] = {'volume_id': volume_id}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "volume", [])
    _openstackify_volume_display_name(r)
    return r


def snf_create_volume(cls, req, name, size):
    """Synnefo: Create a volume"""
    project_id = req.environ.get('HTTP_X_PROJECT_ID', None)
    req.environ['service_type'] = 'volume'
    req.environ['method_name'] = 'volumes_post'

    try:
        size = str(int(size))
    except ValueError:
        size = str(int(float(size)))

    req.environ['kwargs'] = {'size': size, 'display_name': name,
                             'volume_type': str(VOLUME_TYPE),
                             'project': project_id}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "volume", {})
    return snf_get_volume_info(cls, req, r['id'])


def snf_delete_volume(cls, req, volume_id):
    """Synnefo:Delete a volume"""
    req.environ['service_type'] = 'volume'
    req.environ['method_name'] = 'volumes_delete'
    req.environ['kwargs'] = {'volume_id': volume_id}
    req.get_response(cls.app)


function_map = {
    'get_volumes': snf_get_volumes,
    'get_volume': snf_get_volume_info,
    'volume_create': snf_create_volume,
    'volume_delete': snf_delete_volume,

}
