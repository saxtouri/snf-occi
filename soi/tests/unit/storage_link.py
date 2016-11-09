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
from soi import storage_link, config
from mock import patch
import webob.exc
from nose.tools import assert_raises


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
    storage_link._openstackify_volumes_info(volumes_before)
    assert volumes_before == volumes_after


@patch('soi.storage_link._openstackify_volumes_info')
@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_all_volume_links(gr, gfr, ovi):
    """Test snf_get_all_volume_links method"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    storage_link.snf_get_all_volume_links(cls, req)
    assert req.environ == dict(
        service_type='volume',
        method_name='volumes_get',
        kwargs={'detail': True}
    )
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'volumes', [])
    ovi.assert_called_once_with('g f r')


@patch('soi.tests.fakes.DummyClass.get_from_response')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_get_server_volume_links(gr, gfr):
    """Test snf_get_server_volume_links method"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    server_id = '1234'
    storage_link.snf_get_server_volume_links(cls, req, server_id)
    assert req.environ == dict(
        service_type='compute',
        method_name='volume_attachment_get',
        kwargs={'server_id': server_id}
    )
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'volumeAttachments', [])


@patch('soi.tests.fakes.DummyClass.get_from_response')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_create_server_volume_link(gr, gfr):
    """Test snf_create_server_volume_link method"""
    setattr(config, "DISABLE_STORAGE_LINK_CREATION", False)
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    server_id = '1234'
    volume_id = '666'
    dev = ""
    project_id = 'a project id'
    req.environ['HTTP_X_PROJECT_ID'] = project_id
    storage_link.snf_create_server_volume_link(cls, req, server_id, volume_id,
                                               dev)
    assert req.environ == dict(
        HTTP_X_PROJECT_ID=project_id,
        service_type='compute',
        method_name='volume_attachment_post',
        kwargs={'server_id': server_id,
                'volume_id': volume_id,
                'device': dev,
                'project': project_id}
    )
    gr.assert_called_once_with(cls.app)
    gfr.assert_called_once_with('my response', 'volumeAttachment', {})


def test_snf_create_server_volume_link_disabled():
    """Test snf_create_server_volume_link method disabled"""
    setattr(config, "DISABLE_STORAGE_LINK_CREATION", True)
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    server_id = '1234'
    volume_id = '666'
    dev = ""
    project_id = 'a project id'
    req.environ['HTTP_X_PROJECT_ID'] = project_id

    assert_raises(webob.exc.HTTPNotImplemented,
                  storage_link.snf_create_server_volume_link, cls, req,
                  server_id, volume_id, dev)


@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_delete_server_volumes_link(gr):
    """Test snf_delete_server_volumes_link method"""
    setattr(config, "DISABLE_STORAGE_LINK_DELETION", False)
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    server_id = '1234'
    volume_id = '666'
    storage_link. snf_delete_server_volumes_link(cls, req, server_id,
                                                 volume_id)
    assert req.environ == dict(
        service_type='compute',
        method_name='volume_attachment_delete',
        kwargs={'server_id': server_id,
                'attachment_id': volume_id}
    )
    gr.assert_called_once_with(cls.app)


def test_snf_delete_server_volumes_link_disabled():
    """Test snf_delete_server_volumes_link method"""
    setattr(config, "DISABLE_STORAGE_LINK_DELETION", True)
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    server_id = '1234'
    volume_id = '666'
    assert_raises(webob.exc.HTTPNotImplemented,
                  storage_link.snf_delete_server_volumes_link, cls, req,
                  server_id, volume_id)
