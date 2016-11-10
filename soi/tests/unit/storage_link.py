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
from soi import storage_link
from soi.tests.utils import clear_disabled_methods_list
from mock import patch

clear_disabled_methods_list()


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


@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_snf_delete_server_volumes_link(gr):
    """Test snf_delete_server_volumes_link method"""

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
