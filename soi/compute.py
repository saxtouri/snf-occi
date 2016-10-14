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


def _openstackify_addresses(addresses, attachments):
    """Adjust server-nics to os-interface format
    This will affect addresses, not attachments, but attachments are used as
    input information
    """
    for att in attachments:
        net_id, mac_addr = att['network_id'], att['mac_address']
        for addr in addresses[net_id]:
            addr.setdefault('net_id', net_id)
            addr.setdefault('OS-EXT-IPS-MAC:mac_addr', mac_addr)


def snf_get_server(cls, req, server_id):
    """Synnefo: server info <server_id>"""
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'servers_get'
    req.environ['kwargs'] = {'server_id': server_id}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "server", {})
    _openstackify_addresses(r['addresses'], r['attachments'])
    return r


def snf_get_flavor(cls, req, flavor_id):
    """Synnefo: flavor info <flavor_id>"""
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'flavors_get'
    req.environ['kwargs'] = {'flavor_id': flavor_id}
    response = req.get_response(cls.app)
    return cls.get_from_response(response, "flavor", {})


def snf_get_image(cls, req, image_id):
    """Synnefo: flavor info <image_id>"""
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'images_get'
    req.environ['kwargs'] = {'image_id': image_id}
    response = req.get_response(cls.app)
    return cls.get_from_response(response, "image", {})


def snf_get_server_volumes_link(cls, req, server_id):
    """Synnefo: server attachments <server_id>"""
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'volume_attachment_get'
    req.environ['kwargs'] = {'server_id': server_id}
    response = req.get_response(cls.app)
    return cls.get_from_response(response, "volumeAttachments", [])


def _openstackify_net_attachments(attachments):
    """OpenStack uses different keys for the same fields"""
    for a in attachments:
        a['net_id'] = a['network_id']
        a['mac_addr'] = a['mac_address']
        a['port_id'] = a['id']
        if a.get('OS-EXT-IPS:type', '') in ('fixed', ):
            fixed_ips, ipv4, ipv6 = {}, a.get('ipv4'), a.get('ipv6')
            if ipv4 or ipv6:
                fixed_ips['ip_address'] = ipv6 or ipv4
            a['fixed_ips'] = fixed_ips


def snf_get_server_net_attachments(cls, req, compute_id):
    """Adjust server-nics to os-interface format"""
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'servers_ips_get'
    req.environ['kwargs'] = {'server_id': compute_id}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, 'attachments', [])
    _openstackify_net_attachments(r)
    return r


def snf_delete_server(cls, req, server_id):
    print 'Deleting VM with id:' + str(server_id)
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'servers_delete'
    req.environ['kwargs'] = {'server_id': server_id}
    req.get_response(cls.app)

function_map = {
    'index': snf_index,
    'get_server': snf_get_server,
    'get_flavors': snf_get_flavors,
    'get_flavor': snf_get_flavor,
    'get_images': snf_get_images,
    'get_image': snf_get_image,
    'get_floating_ip_pools': empty_list_200,
    'get_server_volumes_link': snf_get_server_volumes_link,
    '_get_ports': snf_get_server_net_attachments,
    'delete': snf_delete_server
}
