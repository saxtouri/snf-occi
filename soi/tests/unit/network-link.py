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
from soi import network_links
from soi.tests.utils import clear_disabled_methods_list
from mock import patch

clear_disabled_methods_list()


def test_openstackify_port_response():
    """Test _openstackify_port_response method"""
    info_before = [{u'status': u'ACTIVE',
                    u'updated': u'2016-11-04T15:54:57.092438+00:00',
                    u'network_id': u'57',
                    u'tenant_id': u'7ae413e9-ce5c-4512-9328-1d821bc3e1a8',
                    u'mac_address': u'aa:00:01:59:7d:8e',
                    u'id': u'2907', u'device_id': u'2297'}]

    info_after = [{u'status': u'ACTIVE', 'port_state': u'ACTIVE',
                   u'updated': u'2016-11-04T15:54:57.092438+00:00',
                   u'network_id': u'57', 'net_id': u'57',
                   u'tenant_id': u'7ae413e9-ce5c-4512-9328-1d821bc3e1a8',
                   u'mac_address': u'aa:00:01:59:7d:8e',
                   'mac_addr': u'aa:00:01:59:7d:8e', 'port_id': u'2907',
                   u'id': u'2907', u'device_id': u'2297'}]

    network_links._openstackify_port_response(info_before)
    assert info_before == info_after


def test__openstackify_floating_ips_response():
    """Test _openstackify_floating_ips_response method"""

    info_before = [{'fixed_ip_address': '192.168.0.1',
                    'floating_ip_address': '192.168.0.1'}]

    info_after = [
        {
            'fixed_ip_address': '192.168.0.1',
            'floating_ip_address': '192.168.0.1',
            'fixed_ip': '192.168.0.1',
            'ip': '192.168.0.1'
        }
    ]

    network_links._openstackify_floating_ips_response(info_before)
    assert info_before == info_after


@patch('soi.network_links._openstackify_floating_ips_response',
       return_value='res')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_list_floating_ips(gr, gfr, _osnr):
    """Test snf_list_networks method"""

    cls, req = fakes.DummyClass(), fakes.FakeReq()
    network_links.snf_list_floating_ips(cls, req)
    assert req.environ == dict(
        service_type='network',
        method_name='floatingips_get',
        kwargs={'success': 200}
    )
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'floatingips', [])
    _osnr.assert_called_once_with('g f r')


ports = [{u'status': u'ACTIVE',
          u'updated': u'2016-11-04T15:54:57.092438+00:00',
          u'user_id': u'7ae413e9-ce5c-4512-9328-1d821bc3e1a8',
          u'name': u'', u'admin_state_up': u'True', u'network_id': u'57',
          u'tenant_id': u'7ae413e9-ce5c-4512-9328-1d821bc3e1a8',
          u'created': u'2016-11-04T15:54:06.369182+00:00',
          u'device_owner': u'vm', u'mac_address': u'aa:00:01:59:7d:8e',
          u'fixed_ips': [{u'subnet': u'57',
                          u'ip_address': u"2001:648:2ffc:1226:a800:1ff"
                          ":fe59:7d8e"}], u'id': u'2907',
          u'security_groups': [], u'device_id': u'2297'},

         {u'status': u'ACTIVE',
          u'updated': u'2016-12-13T08:36:37.826693+00:00',
          u'user_id': u'7ae413e9-ce5c-4512-9328-1d821bc3e1a8',
          u'name': u'', u'admin_state_up': u'True', u'network_id': u'57',
          u'tenant_id': u'7ae413e9-ce5c-4512-9328-1d821bc3e1a8',
          u'created': u'2016-12-13T08:35:39.986056+00:00',
          u'device_owner': u'vm', u'mac_address': u'aa:00:01:b1:56:3b',
          u'fixed_ips': [{u'subnet': u'57',
                          u'ip_address': u"2001:648:2ffc:1226:a800:1ff:"
                          "feb1:563b"}], u'id': u'3006',
          u'security_groups': [], u'device_id': u'2349'},
         {u'status': u'ACTIVE',
          u'updated': u'2016-12-14T15:05:16.176927+00:00',
          u'user_id': u'7ae413e9-ce5c-4512-9328-1d821bc3e1a8',
          u'name': u'', u'admin_state_up': u'True', u'network_id': u'1',
          u'tenant_id': u'7ae413e9-ce5c-4512-9328-1d821bc3e1a8',
          u'created': u'2016-12-14T15:05:11.073822+00:00',
          u'device_owner': u'vm', u'mac_address': u'aa:0c:f1:6a:f7:70',
          u'fixed_ips': [{u'subnet': u'52',
                          u'ip_address': u'62.217.123.20'}],
          u'id': u'3045', u'security_groups': [], u'device_id': u'2349'}]


def test_filter_ports():

    server_id = '2297'
    _ports = ports
    _ports = network_links._filter_ports(_ports, server_id)
    assert len(_ports) == 1

    server_id = '2349'
    _ports = ports
    _ports = network_links._filter_ports(_ports, server_id)
    assert len(_ports) == 2


@patch('soi.network_links._openstackify_port_response', return_value='res')
@patch('soi.network_links._filter_ports', return_value='f p')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value=[])
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_ports(gr, gfr, _fp, _osnr):
    """Test snf_get_ports method"""

    cls, req = fakes.DummyClass(), fakes.FakeReq()
    server_id = 'srv_id'
    network_links.snf_get_ports(cls, req, server_id)
    assert req.environ == dict(
        service_type='network',
        method_name='ports_get',
        kwargs={'success': 200, 'device_id': server_id}
    )
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'ports', [])
    _fp.assert_called_once_with([], server_id)
    _osnr.assert_called_once_with('f p')


@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test__snf_create_floating_ip(gr, gfr):
    """Test _snf_create_floating_ip method"""

    cls, req = fakes.DummyClass(), fakes.FakeReq()
    project_id = 'a project id'
    req.environ['HTTP_X_PROJECT_ID'] = project_id

    network_links._snf_create_floating_ip(cls, req)

    data = {'floatingip': {'floating_network_id': None,
                           'floating_ip_address': '',
                           'project': project_id}}

    assert req.environ == dict(
        HTTP_X_PROJECT_ID=project_id,
        service_type='network',
        method_name='floatingips_post',
        kwargs={'success': 200, 'json_data': data}
    )

    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'floatingip', {})


floating_ips_listing_results = [{'port_id': None,
                                 'floating_network_id': 'test',
                                 'floating_ip_address': 'test'}]


@patch('ooi.api.helpers.OpenStackHelper._build_link', return_value='g f r')
@patch('soi.network_links._snf_create_port_public_net',
       return_value='my response')
@patch('soi.network_links.snf_list_floating_ips',
       return_value=floating_ips_listing_results)
def test__snf_allocate_floating_ip1(lsfips, cppn, bl):
    """Test _snf_allocate_floating_ip method
    Case of existing floating ips
    """
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    network_id = device_id = 'test_id'
    pool = None
    network_links.snf_allocate_floating_ip(cls, req, network_id, device_id,
                                           pool)
    lsfips.assert_called_once_with(cls, req)
    floating_network_id = floating_ips_listing_results[0]["floating_"
                                                          "network_id"]
    floating_ip_address = floating_ips_listing_results[0]["floating_ip_"
                                                          "address"]

    cppn.assert_called_once_with(cls, req, floating_network_id, device_id,
                                 floating_ip_address)
    bl.assert_called_once_with(floating_network_id, device_id,
                               floating_ip_address, floating_network_id)


floating_ips_listing_results2 = [{'port_id': 'test',
                                  'floating_network_id': 'test',
                                  'floating_ip_address': 'test'}]
create_floating_ip_results = {'floating_network_id': 'test',
                              'floating_ip_address': 'test'}


@patch('ooi.api.helpers.OpenStackHelper._build_link', return_value='g f r')
@patch('soi.network_links._snf_create_port_public_net',
       return_value='my response')
@patch('soi.network_links._snf_create_floating_ip',
       return_value=create_floating_ip_results)
@patch('soi.network_links.snf_list_floating_ips',
       return_value=floating_ips_listing_results2)
def test__snf_allocate_floating_ip2(lsfips, cfips, cppn, bl):
    """Test _snf_allocate_floating_ip method
    Case of none existing floating ips
    """
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    network_id = device_id = 'test_id'
    pool = None
    network_links.snf_allocate_floating_ip(cls, req, network_id, device_id,
                                           pool)
    lsfips.assert_called_once_with(cls, req)
    cfips.assert_called_once_with(cls, req)
    floating_network_id = create_floating_ip_results['floating_network_id']
    floating_ip_address = create_floating_ip_results['floating_ip_address']

    cppn.assert_called_once_with(cls, req, floating_network_id, device_id,
                                 floating_ip_address)
    bl.assert_called_once_with(floating_network_id, device_id,
                               floating_ip_address, floating_network_id)


cppnet_results = {'id': 'test', 'status': 'test', 'mac_address': 'test',
                  'port_id': 'test',
                  'network_id': 'test', 'fixed_ips': [{'ip_address': 'test'}]}


@patch('ooi.api.helpers.OpenStackHelper._build_link', return_value='g f r')
@patch('soi.tests.fakes.DummyClass.get_from_response',
       return_value=cppnet_results)
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test__snf_create_port_private_net(gr, gfr, bl):
    """Test snf_create_port_private_net method"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    network_id = device_id = 'test_id'
    data = {'port': {'network_id': network_id, 'device_id': device_id}}

    network_links._snf_create_port_private_net(cls, req, network_id, device_id)
    assert req.environ == dict(
        service_type='network',
        method_name='ports_post',
        kwargs={'success': 201, 'json_data': data}
    )
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'port', {})

    bl.assert_called_once_with(cppnet_results['network_id'], device_id,
                               cppnet_results['fixed_ips'][0]['ip_address'],
                               ip_id=cppnet_results['id'],
                               mac=cppnet_results['mac_address'],
                               state=cppnet_results['status'])


@patch('soi.network_links.snf_allocate_floating_ip',
       return_value='my response')
@patch('soi.network.snf_show_network', return_value={'public': True})
def test_snf_create_network_link(sn, allocfip):
    """Test snf_create_network_link
    Case of public network
    """
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    network_id = device_id = 'test_id'
    network_links.snf_create_network_link(cls, req, network_id, device_id)

    sn.assert_called_once_with(cls, req, network_id)
    allocfip.assert_called_once_with(cls, req, network_id, device_id,
                                     pool=None)


@patch('soi.network_links._snf_create_port_private_net',
       return_value='my response')
@patch('soi.network.snf_show_network', return_value={'public': False})
def test_snf_create_network_link2(sn, cppnet):
    """Test snf_create_network_link
    Case of private network
    """
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    network_id = device_id = 'test_id'
    network_links.snf_create_network_link(cls, req, network_id, device_id)

    sn.assert_called_once_with(cls, req, network_id)
    cppnet.assert_called_once_with(cls, req, network_id, device_id)


@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test__snf_delete_port(gr):
    """Test _snf_delete_port method"""

    cls, req = fakes.DummyClass(), fakes.FakeReq()
    compute_id = ip_id = 'test'
    network_links._snf_delete_port(cls, req, compute_id, ip_id)
    assert req.environ == dict(
        service_type='network',
        method_name='ports_delete',
        kwargs={'port_id': ip_id, 'server_id': compute_id, 'success': 204}
    )
    gr.assert_called_once_with(cls.app)

ports_data = [{'status': u'ACTIVE',
               'net_id': u'57',
               'port_state': u'ACTIVE',
               'mac_addr': u'aa:00:01:59:7d:8e',
               'port_id': 'test_id',
               'id': u'2907', 'device_id': '2297'}]


@patch('soi.network_links._snf_delete_port', return_value='my response')
@patch('soi.network_links.snf_get_ports', return_value=ports_data)
def test_snf_delete_network_link(gp, dp):
    """Test snf_delete_network_link method"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    compute_id = port_id = 'test_id'
    network_links.snf_delete_network_link(cls, req, compute_id, port_id)
    gp.assert_called_once_with(cls, req, compute_id)
    dp.assert_called_once_with(cls, req, compute_id, port_id)
