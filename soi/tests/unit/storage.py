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
from soi import storage, config
from mock import patch


def test_openstackify_volumes_info():
    """Test _openstackify_volumes_info helper method"""
    volumes_before = [{'status': 'in_use',
                       'user_id': '3141d95c-81fb-472f-a31a-acb4f6998b06',
                       'display_name': 'name1',
                       'attachments': [{'server_id': '9499',
                                        'device_index': 0,
                                        'volume_id': '5609'}]},
                      {'status': 'in_use',
                       'user_id': '3141d95c-81fb-472f-a31a-acb4f6998b06',
                       'display_name': 'name2',
                       'attachments': [{'server_id': '681849',
                                        'device_index': 0,
                                        'volume_id': '67712'}]
                       }]

    volumes_after = [{'status': 'in_use',
                      'user_id': '3141d95c-81fb-472f-a31a-acb4f6998b06',
                      'display_name': 'name1',
                      'displayName': 'name1',
                      'attachments': [{
                          'server_id': '9499',
                          'serverId': '9499',
                          'device_index': 0,
                          'device': 0,
                          'volume_id': '5609',
                          'volumeId': '5609'
                      }]},
                     {'status': 'in_use',
                      'user_id': '3141d95c-81fb-472f-a31a-acb4f6998b06',
                      'display_name': 'name2',
                      'displayName': 'name2',
                      'attachments': [{
                          'server_id': '681849',
                          'device_index': 0,
                          'volume_id': '67712',
                          'serverId': '681849',
                          'device': 0,
                          'volumeId': '67712'
                      }]
                      }]
    storage._openstackify_volumes_info(volumes_before)
    assert volumes_before == volumes_after


@patch('soi.storage._openstackify_volumes_info')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_volumes(gr, gfr, _ovdns):
    """Test snf_get_volumes method"""
    DISABLED_METHODS = ()
    setattr(config, 'DISABLED_METHODS', DISABLED_METHODS)
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    storage.snf_get_volumes(cls, req)
    assert req.environ == dict(
        service_type='volume',
        method_name='volumes_get',
        kwargs={'detail': True}
    )
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'volumes', [])
    _ovdns.assert_called_once_with('g f r')


def test_openstackify_volume_display_name():
    """Test _openstackify_volume_display_name helper method"""
    response_result = {'display_name': 'boot volume', 'id': '5609'}

    storage._openstackify_volume_display_name(response_result)
    assert response_result['displayName']


@patch('soi.storage._openstackify_volume_display_name')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_volume(gr, gfr, _ovdn):
    """Test snd_get_volume method"""
    DISABLED_METHODS = ()
    setattr(config, 'DISABLED_METHODS', DISABLED_METHODS)
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    volume_id = 'volume_id'
    storage.snf_get_volume_info(cls, req, volume_id)
    assert req.environ == dict(
        service_type='volume',
        method_name='volumes_get',
        kwargs={'volume_id': volume_id})
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'volume', [])
    _ovdn.assert_called_once_with('g f r')


@patch('soi.storage.snf_get_volume_info')
@patch(
    'soi.tests.fakes.DummyClass.get_from_response',
    return_value={'id': 'some id'})
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_create_volume(gr, gfr, gvi):
    """Test snf_create_volume method"""
    DISABLED_METHODS = ()
    setattr(config, 'DISABLED_METHODS', DISABLED_METHODS)
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    project_id = 'a project id'
    name, size = 'OCCI Volume', '100'
    req.environ['HTTP_X_PROJECT_ID'] = project_id
    storage.snf_create_volume(cls, req, name, size)
    assert req.environ == dict(
        HTTP_X_PROJECT_ID=project_id,
        service_type='volume',
        method_name='volumes_post',
        kwargs={'size': size, 'display_name': name,
                'volume_type': '2',
                'project': project_id})
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'volume', {})
    gvi.assert_called_once_with(cls, req, 'some id')


@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_delete_volume(gr):
    """Test snf_delete_volume """
    DISABLED_METHODS = ()
    setattr(config, 'DISABLED_METHODS', DISABLED_METHODS)
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    volume_id = 'a volume id'
    storage.snf_delete_volume(cls, req, volume_id)
    assert req.environ == dict(
        service_type='volume',
        method_name='volumes_delete',
        kwargs={'volume_id': volume_id})
    gr.assert_called_once_with(cls.app)
