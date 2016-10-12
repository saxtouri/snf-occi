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


def patch_class_methods(cls, function_map):
    """Replace the methods of a class with different ones
    :param cls: the class to patch its methods
    :param function_map: {'class_method_name': replace_method, ...}
    """
    for method_name, new_method in function_map.items():
        setattr(cls, method_name, new_method)


def empty_list_200(cls, req):
    """return OK 200 and empty list"""
    req.environ['service_type'] = 'mock'
    req.environ['method_name'] = 'empty_list'
    response = req.get_response(cls.app)
    return cls.get_from_response(response, 'empty list', [])
