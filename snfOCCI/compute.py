# Copyright (C) 2012-2016 GRNET S.A.
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


from snfOCCI import config

from kamaki.clients import ClientError

from occi.backend import ActionBackend, KindBackend, MixinBackend
from occi.extensions import infrastructure
from occi.exceptions import HTTPError
from base64 import b64encode, b64decode
import yaml

# Compute Backend for snf-occi-server


class MyBackend(KindBackend, ActionBackend):
    """Update and Replace compute instances not supported by Cyclades"""

    def update(self, old, new, extras):
        raise HTTPError(501, "Update is currently no applicable")

    def replace(self, old, new, extras):
        raise HTTPError(501, "Replace is currently no applicable")


class SNFBackend(MixinBackend, ActionBackend):

    pass


class ComputeBackend(MyBackend):
    """Backend for Cyclades/Openstack compute instances"""

    def create(self, entity, extras):
        """Create new compute instance"""
        try:

            snf_network = extras['snf_network']
            snf_compute = extras['snf_compute']

            for mixin in entity.mixins:
                print mixin
                if 'occi.core.id' in mixin.attributes:
                    if mixin.related[0].term == 'os_tpl':
                        image_id = mixin.attributes['occi.core.id']
                    elif mixin.related[0].term == 'resource_tpl':
                        flavor = mixin
                        flavor_id = mixin.attributes['occi.core.id']

            kwargs = dict(
                project_id=extras.get('snf_project', None),
                personality=[])

            key = 'org.openstack.compute.user_data'
            cont = key in entity.attributes
            user_data = b64decode(entity.attributes[key]) if cont else None
            if user_data:
                print "Prepare to inject user data to VM"
                kwargs['personality'].append({
                    'contents': b64encode(user_data),
                    'path': '/var/lib/cloud/seed/nocloud-net/user-data'})

            key = 'org.openstack.credentials.publickey.data'
            cont = key in entity.attributes
            user_pub_key = entity.attributes[key] if cont else None
            if user_pub_key:
                print "Prepare to inject public key to VM"
                pub_key = yaml.dump({'public-keys': user_pub_key})
                kwargs['personality'].append({
                    'contents': b64encode(pub_key),
                    'path': '/var/lib/cloud/seed/nocloud-net/meta-data'})

            print 'Create a server...'
            vm_name = entity.attributes['occi.core.title']
            for retries in range(2):
                try:
                    info = snf_compute.create_server(
                        vm_name, flavor_id, image_id, **kwargs)
                    break
                except ClientError as ce:
                    if ce.status in (409, ):
                        print '{ce}, create an IP and retry'.format(ce=ce)
                        snf_network.create_floatingip(**kwargs)
                    else:
                        raise ce

            entity.attributes.update((
                ('occi.compute.state', 'inactive'),
                ('occi.core.id', str(info['id'])),
                ('occi.compute.architecture', config.COMPUTE['arch']),
                (
                    'occi.compute.cores',
                    flavor.attributes['occi.compute.cores']),
                (
                    'occi.compute.memory',
                    flavor.attributes['occi.compute.memory']), ))

            entity.actions = [
                infrastructure.STOP,
                infrastructure.SUSPEND,
                infrastructure.RESTART]

            info['adminPass'] = ""
            print 'info: {0}'.format(info)
            networkIDs, addr = info['addresses'].keys(), ''
            if networkIDs:
                addr = str(info['addresses'][networkIDs[0]][0]['addr'])
            entity.attributes['occi.compute.hostname'] = addr

        except (UnboundLocalError, KeyError):
            raise HTTPError(406, 'Missing details about compute instance')

    def retrieve(self, entity, extras):
        """Triggering cyclades to retrieve up to date information"""
        snf_compute = extras['snf_compute']

        vm_id = int(entity.attributes['occi.core.id'])
        vm_info = snf_compute.get_server_details(vm_id)
        vm_state = vm_info['status']

        status_dict = dict(
            ACTIVE='active', STOPPED='inactive', REBOOT='inactive',
            ERROR='inactive', BUILD='inactive', DELETED='inactive',
            UNKNOWN='inactive', )

        entity.attributes['occi.compute.state'] = status_dict[vm_state]

        if vm_state in ('ERROR', ):
            raise HTTPError(500, 'ERROR building the compute instance')
        else:
            if entity.attributes['occi.compute.state'] == 'inactive':
                entity.actions = [infrastructure.START]
            if entity.attributes['occi.compute.state'] == 'active':
                entity.actions = [
                    infrastructure.STOP,
                    infrastructure.SUSPEND,
                    infrastructure.RESTART]

    def delete(self, entity, extras):
        """Deleting compute instance"""
        snf_compute = extras['snf_compute']
        vm_id = int(entity.attributes['occi.core.id'])
        snf_compute.delete_server(vm_id)
        print "Deleting VM" + str(vm_id)

    def get_vm_actions(self, entity, vm_state):
        actions = []
        status_dict = dict(
            ACTIVE='active', STOPPED='inactive', REBOOT='inactive',
            ERROR='inactive', BUILD='inactive', DELETED='inactive',
            UNKNOWN='inactive', )

        if vm_state in status_dict:
            entity.attributes['occi.compute.state'] = status_dict[vm_state]
            if vm_state in ('ACTIVE', ):
                actions.append(infrastructure.STOP)
                actions.append(infrastructure.RESTART)
            elif vm_state in ('STOPPED', ):
                actions.append(infrastructure.START)
            return actions
        else:
            raise HTTPError(500, 'Undefined status of the VM')

    def action(self, entity, action, attributes, extras):
        """Triggering action to compute instances"""
        snf_compute = extras['snf_compute']

        vm_id = int(entity.attributes['occi.core.id'])
        vm_info = snf_compute.get_server_details(vm_id)
        vm_state = vm_info['status']

        # Define the allowed actions depending on the state of the VM
        entity.actions = self.get_vm_actions(entity, vm_state)

        if vm_state == 'ERROR':
            raise HTTPError(500, 'ERROR building the compute instance')
        else:
            if action not in entity.actions:
                raise AttributeError(
                    "Action not applicable for VM with status {0}".format(
                        vm_state))
            elif action == infrastructure.START:
                print "Starting VM {0}".format(vm_id)
                snf_compute.start_server(vm_id)
            elif action == infrastructure.STOP:
                print "Stopping VM {0}".format(vm_id)
                snf_compute.shutdown_server(vm_id)
            elif action == infrastructure.RESTART:
                print "Restarting VM {0}".format(vm_id)
                snf_compute.reboot_server(vm_id)
            elif action == infrastructure.SUSPEND:
                raise HTTPError(501, "Actions not applicable")
