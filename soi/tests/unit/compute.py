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
from soi import compute
from soi.tests.utils import clear_disabled_methods_list
from mock import patch
from base64 import b64encode

clear_disabled_methods_list()


@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_index(gr, gfr):
    """Test snf_index"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    r = compute.snf_index(cls, req)
    assert r == 'g f r'
    assert req.environ == dict(
        service_type='compute',
        method_name='servers_get')
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'servers', [])


@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_flavors(gr, gfr):
    """Test snf_get_flavors"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    r = compute.snf_get_flavors(cls, req)
    assert r == 'g f r'
    assert req.environ == dict(
        service_type='compute',
        method_name='flavors_get',
        kwargs=dict(detail=True))
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'flavors', [])


@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_images(gr, gfr):
    """Test snf_get_images"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    r = compute.snf_get_images(cls, req)
    assert r == 'g f r'
    assert req.environ == dict(
        service_type='compute',
        method_name='images_get',
        kwargs=dict(detail=True))
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'images', [])


def test__openstackify_addresses():
    """Test _openstackify_addresses"""
    addresses = {
        '12345': [{
            'version': '4',
            'addr': '123.45.67.89',
            'OS-EXT-IPS:type': 'floating',
        }, ],
        '67890': [{
            'version': '6',
            'addr': '2001:123:5gf6:6789:a800:ff:dast:434d',
            'OS-EXT-IPS:type': 'fixed',
        }, ],
    }
    attachments = [
        {
            'network_id': '12345',
            'mac_address': 'a mac address',
            'id': 'an attachment id',
            'firewallProfile': 'DISABLED',
            'OS-EXT-IPS:type': 'floating',
            'ipv4': '123.45.67.89',
            'ipv6': '',
        },
        {
            'network_id': '67890',
            'mac_address': 'another mac address',
            'id': 'another attachment id',
            'firewallProfile': 'DISABLED',
            'OS-EXT-IPS:type': 'fixed',
            'ipv4': '',
            'ipv6': '2001:123:5gf6:6789:a800:ff:dast:434d',
        },
    ]
    expected_addresses = {
        '12345': [{
            'version': '4',
            'addr': '123.45.67.89',
            'OS-EXT-IPS:type': 'floating',
            'net_id': '12345',
            'OS-EXT-IPS-MAC:mac_addr': 'a mac address',
        }, ],
        '67890': [{
            'version': '6',
            'addr': '2001:123:5gf6:6789:a800:ff:dast:434d',
            'OS-EXT-IPS:type': 'fixed',
            'net_id': '67890',
            'OS-EXT-IPS-MAC:mac_addr': 'another mac address',
        }, ],
    }
    compute._openstackify_addresses(addresses, attachments)
    assert addresses == expected_addresses


_response = {
    'addresses': 'some addresses', 'attachments': 'some attachments'
}


@patch('soi.compute._openstackify_addresses')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value=_response)
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_server(gr, gfr, _oa):
    """Test snf_get_server"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    r = compute.snf_get_server(cls, req, 'my server id')
    assert r == _response
    assert req.environ == dict(
        service_type='compute',
        method_name='servers_get',
        kwargs=dict(server_id='my server id'))
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'server', {})
    _oa.assert_called_once_with(
        _response['addresses'], _response['attachments'])


@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_flavor(gr, gfr):
    """Test snf_get_flavor"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    r = compute.snf_get_flavor(cls, req, 'my flavor id')
    assert r == 'g f r'
    assert req.environ == dict(
        service_type='compute',
        method_name='flavors_get',
        kwargs=dict(flavor_id='my flavor id'))
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'flavor', {})


@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_image(gr, gfr):
    """Test snf_get_image"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    r = compute.snf_get_image(cls, req, 'my image id')
    assert r == 'g f r'
    assert req.environ == dict(
        service_type='compute',
        method_name='images_get',
        kwargs=dict(image_id='my image id'))
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'image', {})


@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_server_volume_links(gr, gfr):
    """Test snf_get_server_volume_links"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    r = compute.snf_get_server_volumes_link(cls, req, 'my server id')
    assert r == 'g f r'
    assert req.environ == dict(
        service_type='compute',
        method_name='volume_attachment_get',
        kwargs=dict(server_id='my server id'))
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'volumeAttachments', [])


def test__openstackify_net_attachments():
    """Test _openstackify_net_attachments"""
    input_ = [
        {
            'network_id': '12345',
            'mac_address': 'a mac address',
            'id': 'an attachment id',
            'firewallProfile': 'DISABLED',
            'OS-EXT-IPS:type': 'floating',
            'ipv4': '123.45.67.89',
            'ipv6': '',
        },
        {
            'network_id': '67890',
            'mac_address': 'another mac address',
            'id': 'another attachment id',
            'firewallProfile': 'DISABLED',
            'OS-EXT-IPS:type': 'fixed',
            'ipv4': '',
            'ipv6': '2001:123:5gf6:6789:a800:ff:dast:434d',
        },
    ]
    expected_output = [
        {
            'network_id': '12345',
            'net_id': '12345',
            'mac_address': 'a mac address',
            'mac_addr': 'a mac address',
            'id': 'an attachment id',
            'port_id': 'an attachment id',
            'firewallProfile': 'DISABLED',
            'OS-EXT-IPS:type': 'floating',
            'ipv4': '123.45.67.89',
            'ipv6': '',
        },
        {
            'network_id': '67890',
            'net_id': '67890',
            'mac_address': 'another mac address',
            'mac_addr': 'another mac address',
            'id': 'another attachment id',
            'port_id': 'another attachment id',
            'firewallProfile': 'DISABLED',
            'OS-EXT-IPS:type': 'fixed',
            'ipv4': '',
            'ipv6': '2001:123:5gf6:6789:a800:ff:dast:434d',
            'fixed_ips': {
                'ip_address': '2001:123:5gf6:6789:a800:ff:dast:434d'},
        },
    ]
    compute._openstackify_net_attachments(input_)
    assert input_ == expected_output


@patch('soi.compute._openstackify_net_attachments')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_server_net_attachments(gr, gfr, _ona):
    """Test snf_get_server_net_attachments"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    r = compute.snf_get_server_net_attachments(cls, req, 'my server id')
    assert r == 'g f r'
    assert req.environ == dict(
        service_type='compute',
        method_name='servers_ips_get',
        kwargs=dict(server_id='my server id'))
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'attachments', [])
    _ona.assert_called_once_with('g f r')


@patch('soi.compute._openstackify_addresses')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value=_response)
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_create_server(gr, gfr, _oa):
    """Test snf_create_server"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    req.environ['HTTP_X_PROJECT_ID'] = 'a project id'
    args = ('a name', 'an image', 'a flavor')
    r = compute.snf_create_server(cls, req, *args)
    assert r == _response
    assert req.environ == dict(
        HTTP_X_PROJECT_ID='a project id',
        service_type='compute',
        method_name='servers_post',
        kwargs=dict(json_data=dict(server=dict(
            name='a name', imageRef='an image', flavorRef='a flavor',
            project='a project id'))))
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'server', {})
    _oa.assert_called_once_with(
        _response['addresses'], _response['attachments'])


def test__get_personality():
    """Test personality syntax method"""
    image = dict(id='some id', metadata=dict(users='root'))
    public_key = 'some public key'
    pkey = b64encode(public_key)
    constant = '/var/lib/cloud/seed/nocloud-net/meta-data'
    suffix = '.ssh/authorized_keys'

    r = compute._get_personality(image, public_key)
    assert r == [
        {'contents': pkey, 'path': constant},
        {
            'contents': pkey, 'path': '/root/{0}'.format(suffix),
            'owner': 'root', 'group': 'root', 'mode': 0600
        }
    ]

    image['metadata']['users'] = 'user'
    r = compute._get_personality(image, public_key)
    assert r == [
        {'contents': pkey, 'path': constant},
        {
            'contents': pkey, 'path': '/home/user/{0}'.format(suffix),
            'owner': 'user', 'group': 'user', 'mode': 0600
        }
    ]

    image['metadata']['users'] = 'root user'
    r = compute._get_personality(image, public_key)
    assert r == [
        {'contents': pkey, 'path': constant},
        {
            'contents': pkey, 'path': '/root/{0}'.format(suffix),
            'owner': 'root', 'group': 'root', 'mode': 0600
        },
        {
            'contents': pkey, 'path': '/home/user/{0}'.format(suffix),
            'owner': 'user', 'group': 'user', 'mode': 0600
        }
    ]


@patch('soi.compute.snf_get_image', return_value='some image')
@patch('soi.compute._get_personality', return_value=['some key'])
@patch('soi.compute._openstackify_addresses')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value=_response)
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_create_server_with_pk_no_key_name(gr, gfr, _oa, gp, snfci):
    """Test snf_create_server with pk no key name"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    req.environ['soi:public_keys'] = {'key_name': 'some key'}
    req.environ['HTTP_X_PROJECT_ID'] = 'a project id'
    args = ('a name', 'an image', 'a flavor')
    r = compute.snf_create_server(cls, req, *args)
    assert r == _response

    assert req.environ == {
        'HTTP_X_PROJECT_ID': 'a project id',
        'service_type': 'compute',
        'method_name': 'servers_post',
        'soi:public_keys':  {'key_name': 'some key'},
        'kwargs': dict(json_data=dict(server=dict(
            name='a name', imageRef='an image', flavorRef='a flavor',
            project='a project id')))}

    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'server', {})
    _oa.assert_called_once_with(
        _response['addresses'], _response['attachments'])


@patch('soi.compute.snf_get_image', return_value='some image')
@patch('soi.compute._get_personality', return_value=['some key'])
@patch('soi.compute._openstackify_addresses')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value=_response)
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_create_server_with_pk(gr, gfr, _oa, gp, snfci):
    """Test snf_create_server with pk"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    req.environ['soi:public_keys'] = {'key_name': 'some key'}
    req.environ['HTTP_X_PROJECT_ID'] = 'a project id'
    args = ('a name', 'an image', 'a flavor')
    r = compute.snf_create_server(cls, req, *args, key_name='key_name')
    assert r == _response

    assert req.environ == {
        'HTTP_X_PROJECT_ID': 'a project id',
        'service_type': 'compute',
        'method_name': 'servers_post',
        'soi:public_keys':  {'key_name': 'some key'},
        'kwargs': dict(json_data=dict(server=dict(
            name='a name', imageRef='an image', flavorRef='a flavor',
            project='a project id', personality=['some key', ])))}
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'server', {})
    _oa.assert_called_once_with(
        _response['addresses'], _response['attachments'])


@patch('soi.compute.snf_get_image', return_value='some image')
@patch('soi.compute._openstackify_addresses')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value=_response)
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_create_server_with_user_data(gr, gfr, _oa, snfci):
    """Test snf_create_server with user data"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    req.environ['HTTP_X_PROJECT_ID'] = 'a project id'
    args = ('a name', 'an image', 'a flavor')
    r = compute.snf_create_server(cls, req, *args, user_data='user data')
    assert r == _response

    exp_personlity = {
        "path": "/var/lib/cloud/seed/nocloud-net/user-data",
        "contents": b64encode('user data')
    }

    assert req.environ == {
        'HTTP_X_PROJECT_ID': 'a project id',
        'service_type': 'compute',
        'method_name': 'servers_post',
        'kwargs': dict(json_data=dict(server=dict(
            name='a name', imageRef='an image', flavorRef='a flavor',
            project='a project id', personality=[exp_personlity, ])))}
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'server', {})
    _oa.assert_called_once_with(
        _response['addresses'], _response['attachments'])


@patch('soi.compute.snf_get_image', return_value='some image')
@patch('soi.compute._get_personality', return_value=['some key'])
@patch('soi.compute._openstackify_addresses')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value=_response)
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_create_server_with_full_context(gr, gfr, _oa, gp, snfci):
    """Test snf_create_server with user data"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    req.environ['HTTP_X_PROJECT_ID'] = 'a project id'
    req.environ['soi:public_keys'] = {'key_name': 'some key'}
    args = ('a name', 'an image', 'a flavor')
    r = compute.snf_create_server(
        cls, req, *args, user_data='user data', key_name='key_name')
    assert r == _response

    exp_personlity = {
        "path": "/var/lib/cloud/seed/nocloud-net/user-data",
        "contents": b64encode('user data')
    }

    assert req.environ == {
        'HTTP_X_PROJECT_ID': 'a project id',
        'service_type': 'compute',
        'method_name': 'servers_post',
        'soi:public_keys':  {'key_name': 'some key'},
        'kwargs': dict(json_data=dict(server=dict(
            name='a name', imageRef='an image', flavorRef='a flavor',
            project='a project id',
            personality=[exp_personlity, 'some key', ])))}
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'server', {})
    _oa.assert_called_once_with(
        _response['addresses'], _response['attachments'])


@patch('soi.tests.fakes.FakeReq.get_response')
def test_snf_delete_server(gr):
    """Test snf_delete_server"""

    cls, req = fakes.DummyClass(), fakes.FakeReq()
    compute.snf_delete_server(cls, req, 'my server id')
    assert req.environ == dict(
        service_type='compute',
        method_name='servers_delete',
        kwargs=dict(server_id='my server id'))
    gr.assert_called_once_with(cls.app)


def _test_snf_run_action(action, json_data, gr):
    """used by "test_snf_run_action_* methods"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    compute.snf_run_action(cls, req, action, 'my server id')
    assert req.environ == dict(
        service_type='compute',
        method_name='servers_action_post',
        kwargs=dict(server_id='my server id', json_data=json_data))
    gr.assert_called_once_with(cls.app)


@patch('soi.tests.fakes.FakeReq.get_response')
def test_snf_run_action_start(gr):
    """Test snf_run_action start"""
    _test_snf_run_action('start', {'start': {}}, gr)


@patch('soi.tests.fakes.FakeReq.get_response')
def test_snf_run_action_stop(gr):
    """Test snf_run_action stop"""
    _test_snf_run_action('stop', {'shutdown': {}}, gr)


@patch('soi.tests.fakes.FakeReq.get_response')
def test_snf_run_action_restart(gr):
    """Test snf_run_action restart"""
    _test_snf_run_action('restart', {'reboot': {'type': 'SOFT'}}, gr)


@patch('soi.tests.fakes.FakeReq.get_response')
def test_snf_run_action_suspend(gr):
    """Test snf_run_action suspend"""
    try:
        _test_snf_run_action('suspend', {}, gr)
    except Exception as e:
        from webob.exc import HTTPNotImplemented
        assert isinstance(e, HTTPNotImplemented)


def test_keypair_register():
    """Test keypair_register"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    name, pk = 'key_name', 'rsa-ssa keystuffhere ==user@host'
    compute.keypair_register(cls, req, name, pk)
    assert 'soi:public_keys' in req.environ
    assert req.environ['soi:public_keys'] == {name: pk}

    name0, pk0 = 'key_name0', 'rsa-ssa otherstuffhere ==user@host'
    compute.keypair_register(cls, req, name0, pk0)
    assert req.environ['soi:public_keys'] == {name: pk, name0: pk0}
