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


def _openstackify_volumes_info(volumes):
    """Adjust server_id, device_index, volume_id to OpensStack"""

    for volume in volumes:
        volume['displayName'] = volume['display_name']
        for attachment in volume['attachments']:
            attachment['serverId'] = attachment['server_id']
            attachment['device'] = attachment['device_index']
            attachment['volumeId'] = attachment['volume_id']


def snf_get_all_volume_links(cls, req):
    """Synnefo: get all volume attachments """
    req.environ['service_type'] = 'volume'
    req.environ['method_name'] = 'volumes_get'
    req.environ['kwargs'] = {'detail': True}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "volumes", [])
    _openstackify_volumes_info(r)
    return r


def snf_get_server_volume_links(cls, req, server_id):
    """Synnefo: Get volumes attached to a server"""
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'volume_attachment_get'
    req.environ['kwargs'] = {'server_id': server_id}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "volumeAttachments", [])
    return r


def snf_create_server_volume_link(cls, req, server_id, volume_id,
                                  dev=None):
    """Synnefo: Attach a volume to a server"""
    project_id = req.environ.get('HTTP_X_PROJECT_ID', None)

    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'volume_attachment_post'
    req.environ['kwargs'] = {'server_id': server_id,
                             'volume_id': volume_id,
                             'device': dev,
                             'project': project_id}
    response = req.get_response(cls.app)
    r = cls.get_from_response(response, "volumeAttachment", {})
    return r


def snf_delete_server_volumes_link(cls, req, server_id, volume_id):
    """Synnefo: Delete a volume attachment"""
    req.environ['service_type'] = 'compute'
    req.environ['method_name'] = 'volume_attachment_delete'
    req.environ['kwargs'] = {'server_id': server_id,
                             'attachment_id': volume_id}
    req.get_response(cls.app)


function_map = {
    'get_volumes': snf_get_all_volume_links,
    'get_server_volumes_link': snf_get_server_volume_links,
    'create_server_volumes_link': snf_create_server_volume_link,
    'delete_server_volumes_link': snf_delete_server_volumes_link,
}
