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

from soi.utils import check_activation


def _openstackify_port_response(data):
    """A helper method for openstackifying synnefo port responses"""
    for port in data:
        port['mac_addr'] = port['mac_address']
        port['port_state'] = port['status']
        port['net_id'] = port['network_id']
        port['port_id'] = port['id']


def _openstackify_floating_ips_response(data):
    """A helper method for openstackifying synnefo floating ips responses"""
    for fips in data:
        fips['fixed_ip'] = fips['fixed_ip_address']
        fips['ip'] = fips['floating_ip_address']


@check_activation
def snf_list_floating_ips(cls, req):
    """Synnefo list floating ips method"""
    req.environ['service_type'] = 'network'
    req.environ['method_name'] = 'floatingips_get'
    req.environ['kwargs'] = {'success': 200}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "floatingips", [])
    _openstackify_floating_ips_response(r)
    return r


def _filter_ports(ports, device_id):
    return [port for port in ports if 'device_id' in port
            and port['device_id'] == device_id]


@check_activation
def snf_get_ports(cls, req, device_id):
    """Synnefo get ports method using server id"""
    req.environ['service_type'] = 'network'
    req.environ['method_name'] = 'ports_get'
    req.environ['kwargs'] = {'success': 200, 'device_id': device_id}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "ports", [])
    filtered_data = _filter_ports(r, device_id)
    _openstackify_port_response(filtered_data)
    return filtered_data


function_map = {
    '_get_ports': snf_get_ports,
    'get_floating_ips': snf_list_floating_ips,
}
