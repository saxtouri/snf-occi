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
from soi.network import snf_show_network
from ooi.api.helpers import OpenStackHelper
from ooi import exception


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


def _snf_create_floating_ip(cls, req):
    """Synnefo create floating ip method"""
    req.environ['service_type'] = 'network'
    req.environ['method_name'] = 'floatingips_post'

    project_id = req.environ['HTTP_X_PROJECT_ID']
    data = {'floatingip': {'floating_network_id': None,
                           'floating_ip_address': '',
                           'project': project_id}}

    req.environ['kwargs'] = {'success': 200, 'json_data': data}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "floatingip", {})
    return r


def _snf_create_port_public_net(cls, req, network_id, device_id, fixed_ip):
    """Synnefo create port between a public net and a server"""
    req.environ['service_type'] = 'network'
    req.environ['method_name'] = 'ports_post'
    data = {'port': {'network_id': network_id, 'device_id': device_id,
            'fixed_ips': [{'ip_address': fixed_ip}]}}

    req.environ['kwargs'] = {'success': 201, 'json_data': data}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "port", {})
    return r


@check_activation
def snf_allocate_floating_ip(cls, req, network_id, device_id, pool=None):
    """Synnefo floating ip allocation method"""
    floating_ips = snf_list_floating_ips(cls, req)
    floating_ip_address = None
    floating_network_id = None

    for floating_ip in floating_ips:
        if floating_ip['port_id'] is None:
            floating_ip_address = floating_ip['floating_ip_address']
            floating_network_id = floating_ip['floating_network_id']

    if not all((floating_ip_address, floating_network_id,)):
        print 'Could not find any available floating ip, creating one...'
        floating_ip = _snf_create_floating_ip(cls, req)
        floating_network_id = floating_ip['floating_network_id']
        floating_ip_address = floating_ip['floating_ip_address']

    _snf_create_port_public_net(cls, req, floating_network_id, device_id,
                                floating_ip_address)
    try:
        link_public = OpenStackHelper._build_link(floating_network_id,
                                                  device_id,
                                                  floating_ip_address,
                                                  floating_network_id)
    except Exception:
        raise exception.OCCIInvalidSchema()

    return link_public


def _snf_create_port_private_net(cls, req, network_id, device_id):
    """Synnefo create port method between a server and a private network"""
    req.environ['service_type'] = 'network'
    req.environ['method_name'] = 'ports_post'
    data = {'port': {'network_id': network_id, 'device_id': device_id}}

    req.environ['kwargs'] = {'success': 201, 'json_data': data}
    response = req.get_response(cls.app)
    port = cls.get_from_response(response, "port", {})
    for ip in port["fixed_ips"]:
        return OpenStackHelper._build_link(port["network_id"],
                                           device_id,
                                           ip['ip_address'],
                                           ip_id=port["id"],
                                           mac=port['mac_address'],
                                           state=port["status"])


@check_activation
def snf_create_network_link(cls, req, network_id, device_id):
    """Synnefo create network link"""
    net_info = snf_show_network(cls, req, network_id)
    if net_info['public']:
        return snf_allocate_floating_ip(cls, req, network_id, device_id,
                                        pool=None)
    else:
        return _snf_create_port_private_net(cls, req, network_id, device_id)


def _snf_delete_port(cls, req, device_id, ip_id):
    """Synnefo delete port method"""
    req.environ['service_type'] = 'network'
    req.environ['method_name'] = 'ports_delete'
    req.environ['kwargs'] = {'port_id': ip_id,
                             'server_id': device_id,
                             'success': 204}
    req.get_response(cls.app)


@check_activation
def snf_delete_network_link(cls, req, device_id, port_id):
    """
    Synnefo network_link delete method
    :param <device_id>: The server id
    :param <port_id>: The port id
    TODO:wait until port deletion is done
    """
    for port in snf_get_ports(cls, req, device_id):
        if port['port_id'] == port_id and port['net_id']:
            _snf_delete_port(cls, req, device_id, port_id)
            break


function_map = {
    '_get_ports': snf_get_ports,
    'get_floating_ips': snf_list_floating_ips,
    'delete_port': snf_delete_network_link,
    'create_port': snf_create_network_link,
    'assign_floating_ip': snf_allocate_floating_ip
}
