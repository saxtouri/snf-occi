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

from soi.tests import fakes
from soi import network
from soi.tests.utils import clear_disabled_methods_list
from mock import patch

clear_disabled_methods_list()


def test_openstackify_network_response():
    """Test test_openstackify_network_response helper method"""
    info_before = [{u'status': u'ACTIVE', u'router:external': u'True',
                    u'updated': u'2015-01-18T19:02:38.732086+00:00',
                    u'user_id': None, u'name': u'Public IPv4 Network',
                    u'created': u'2011-04-01T00:00:00+00:00',
                    u'deleted': False, u'tenant_id': None,
                    u'shared_to_project': False, u'admin_state_up': u'True',
                    u'id': u'1', u'type': u'IP_LESS_ROUTED',
                    u'subnets': [u'52'], u'shared': u'True',
                    u'SNF:floating_ip_pool': u'True', u'public': u'True'}]

    info_after = [{u'status': u'ACTIVE', 'state': 'active',
                   'label': 'Public IPv4 Network',
                   u'router:external': u'True',
                   u'updated': u'2015-01-18T19:02:38.732086+00:00',
                   u'user_id': None, u'name': u'Public IPv4 Network',
                   u'created': u'2011-04-01T00:00:00+00:00',
                   u'deleted': False, u'tenant_id': None,
                   u'shared_to_project': False, u'admin_state_up': u'True',
                   u'id': u'1', u'type': u'IP_LESS_ROUTED',
                   u'subnets': [u'52'], u'shared': u'True',
                   u'SNF:floating_ip_pool': u'True', u'public': u'True'}]

    network._openstackify_network_response(info_before)
    assert info_before == info_after

    subnet_info = {'ip_version': u'6', 'cidr': u'2001:648:2ffc:1226::/64',
                   'gateway_ip': u'2001:648:2ffc:1226::1'}
    info_before[0].update(subnet_info)
    subnet_info.update({'gateway': u'2001:648:2ffc:1226::1'})
    info_after[0].update(subnet_info)
    network._openstackify_network_response(info_before, extended=True)
    assert info_before == info_after


subnet_info = {'ip_version': u'6', 'cidr': u'2001:648:2ffc:1226::/64',
               'gateway_ip': u'2001:648:2ffc:1226::1'}


@patch('soi.tests.fakes.DummyClass.get_from_response',
       return_value=subnet_info)
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_subnet(gr, gfr):
    """Test snf_get_subnet method"""

    cls, req = fakes.DummyClass(), fakes.FakeReq()
    subnet_id = 'sbnt_id'
    network._snf_get_subnet(cls, req, subnet_id)
    assert req.environ == dict(
        service_type='network',
        method_name='subnets_get',
        kwargs={'subnet_id': subnet_id}
    )
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'subnet', {})

response = {'ip_version': u'6', 'cidr': u'2001:648:2ffc:1226::/64',
            'gateway': u'2001:648:2ffc:1226::1', 'id': 1, 'label': 'label'}


@patch('ooi.api.helpers.OpenStackHelper._build_networks', return_value='bnets')
@patch('soi.network._openstackify_network_response', return_value='res')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_list_networks(gr, gfr, _osnr, bn):
    """Test snf_list_networks method"""

    cls, req = fakes.DummyClass(), fakes.FakeReq()
    network.snf_list_networks(cls, req)
    assert req.environ == dict(
        service_type='network',
        method_name='networks_get'
    )
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'networks', [])
    _osnr.assert_called_once_with('g f r')
    bn.assert_called_once_with('g f r')


@patch('ooi.api.helpers.OpenStackHelper._build_networks', return_value='bnets')
@patch('soi.network._openstackify_network_response', return_value='res')
@patch('soi.tests.fakes.DummyClass.get_from_response',
       return_value={'subnets': []})
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_show_network(gr, gfr, _osnr, bn):
    """Test snf_show_network method"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    net_id = 'network_id'
    network.snf_show_network(cls, req, net_id)
    assert req.environ == dict(
        service_type='network',
        method_name='networks_get',
        kwargs={'network_id': net_id}

    )
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'network', {})
    _osnr.assert_called_once_with([{'subnets': []}], False)
    bn.assert_called_once_with([{'subnets': []}])
    # more testing is needed


@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_delete_network(gr):
    """Test snf_delete_network method"""

    cls, req = fakes.DummyClass(), fakes.FakeReq()
    net_id = 'network_id'
    network.snf_delete_network(cls, req, net_id)
    assert req.environ == dict(
        service_type='network',
        method_name='networks_delete',
        kwargs={'network_id': net_id, 'success': (204,)}

    )
    gr.assert_called_once_with(cls.app)


@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test__snf_create_subnet(gr, gfr):
    """Test _snf_create_subnet method"""

    cls, req = fakes.DummyClass(), fakes.FakeReq()
    net_id = 'network_id'
    cidr = 'address'
    name = 'OCCI subnet'
    network._snf_create_subnet(cls, req, network_id=net_id, cidr=cidr,
                               name=name, allocation_pools=None,
                               gateway_ip=None,
                               subnet_id=None,
                               ipv6=None, enable_dhcp=False)
    data = {'subnet': {'network_id': net_id, 'cidr': cidr,
                       'ip_version': 4, 'name': name,
                       'allocation_pools': None,
                       'gateway_ip': None, 'subnet_id': None,
                       'enable_dhcp': False
                       }
            }
    assert req.environ == dict(
        service_type='network',
        method_name='subnets_post',
        kwargs={'json_data': data, 'success': 201}

    )
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'subnet', {})


@patch('soi.network.snf_show_network')
@patch('soi.network._snf_create_subnet', return_value='create_subnet')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value={'id': 1})
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_create_network(gr, gfr, csn, sn):
    """Test snf_create_network method"""

    cls, req = fakes.DummyClass(), fakes.FakeReq()
    name = 'OCCI Network'
    cidr = 'address'
    project_id = 'a project id'
    req.environ['HTTP_X_PROJECT_ID'] = project_id

    network.snf_create_network(cls, req, name=name, cidr=cidr, gateway=None,
                               ip_version=None)
    data = {'network': {'admin_state_up': True, 'type': 'MAC_FILTERED',
            'name': name, 'project_id': project_id, 'shared': False}}
    assert req.environ == dict(
        HTTP_X_PROJECT_ID=project_id,
        service_type='network',
        method_name='networks_post',
        kwargs={'json_data': data, 'success': 201}

    )
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'network', {})
    csn.assert_called_once_with(cls, req, network_id=1, cidr=cidr,
                                name=name + " subnet",
                                gateway_ip=None, ipv6=False)
    sn.assert_called_once_with(cls, req, 1)
