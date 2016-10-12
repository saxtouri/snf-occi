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

from utils import empty_list_200


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


function_map = {
    'index': snf_index,
    'get_flavors': snf_get_flavors,
    'get_images': snf_get_images,
    'get_floating_ip_pools': empty_list_200,
}
