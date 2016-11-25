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
from ooi.api.helpers import OpenStackHelper


def _openstackify_network_response(nets, extended=False):
    """Openstackifies synnefo network requests' responses"""
    for net in nets:
        net['state'] = net['status'].lower()
        net['label'] = net['name']
        if extended:
            net['gateway'] = net['gateway_ip']


def _snf_get_subnet(cls, req, id):
    """Synnefo get subnet from a network method"""
    """Synnefo network listing method"""
    req.environ['service_type'] = 'network'
    req.environ['method_name'] = 'subnets_get'
    req.environ['kwargs'] = {'subnet_id': id}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "subnet", {})
    return {'ip_version': r['ip_version'], 'gateway_ip': r['gateway_ip'],
            'cidr': r['cidr']}


@check_activation
def snf_list_networks(cls, req):
    """Synnefo network listing method"""
    req.environ['service_type'] = 'network'
    req.environ['method_name'] = 'networks_get'
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "networks", [])
    _openstackify_network_response(r)
    build_networks = getattr(OpenStackHelper, '_build_networks', None)
    return build_networks(r)


@check_activation
def snf_show_network(cls, req, id):
    """Synnefo network retrieve method"""
    req.environ['service_type'] = 'network'
    req.environ['method_name'] = 'networks_get'
    req.environ['kwargs'] = {'network_id': id}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "network", {})

    extended = False
    if r['subnets']:
        subnet_id = r['subnets'][0]
        subnet_info = _snf_get_subnet(cls, req, subnet_id)
        r.update(subnet_info)
        extended = True

    _openstackify_network_response([r], extended)
    build_networks = getattr(OpenStackHelper, '_build_networks', None)
    return build_networks([r])[0]


@check_activation
def snf_delete_network(cls, req, id):
    """Synnefo delete network method"""
    req.environ['service_type'] = 'network'
    req.environ['method_name'] = 'networks_delete'
    req.environ['kwargs'] = {'network_id': id}
    req.get_response(cls.app)


def _snf_create_subnet(cls, req, network_id, cidr, name=None,
                       allocation_pools=None, gateway_ip=None, subnet_id=None,
                       ipv6=None, enable_dhcp=False):
    """Synnefo create subnet method"""
    req.environ['service_type'] = 'network'
    req.environ['method_name'] = 'subnets_post'

    data = {'subnet': {'network_id': network_id, 'cidr': cidr,
                       'ip_version': 6 if ipv6 else 4, 'name': name,
                       'allocation_pools': allocation_pools,
                       'gateway_ip': gateway_ip, 'subnet_id': subnet_id,
                       'enable_dhcp': enable_dhcp
                       }
            }

    req.environ['kwargs'] = {'json_data': data, 'success': 201}
    response = req.get_response(cls.app)
    cls.get_from_response(response, "subnet", {})


@check_activation
def snf_create_network(cls, req, name, cidr,
                       gateway=None, ip_version=None):
    """Synnefo network creation method"""
    req.environ['service_type'] = 'network'
    req.environ['method_name'] = 'networks_post'

    project_id = req.environ['HTTP_X_PROJECT_ID']
    data = {'network': {'admin_state_up': True, 'type': 'MAC_FILTERED',
            'name': name, 'project_id': project_id, 'shared': False}}

    req.environ['kwargs'] = {'json_data': data, 'success': 201}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "network", {})
    _snf_create_subnet(cls, req, network_id=r['id'], cidr=cidr,
                       name=name + " subnet", gateway_ip=gateway,
                       ipv6=True if ip_version == 6 else False)
    return snf_show_network(cls, req, r['id'])


function_map = {
    'list_networks': snf_list_networks,
    'get_network_details': snf_show_network,
    'delete_network': snf_delete_network,
    'create_network': snf_create_network,

}
