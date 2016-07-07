# Copyright (C) 2012-2013 GRNET S.A.
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


from snfOCCI.config import SERVER_CONFIG
from snfOCCI.extensions import snf_addons

from kamaki.clients import ClientError

from occi.backend import ActionBackend, KindBackend, MixinBackend
from occi.core_model import Mixin
from occi.extensions import infrastructure
from occi.exceptions import HTTPError
from base64 import b64encode, b64decode
import json, yaml

# Compute Backend for snf-occi-server


class MyBackend(KindBackend, ActionBackend):

    # Updating and Replacing compute instances not supported by Cyclades

    def update(self, old, new, extras):
        raise HTTPError(501, "Update is currently no applicable")

    def replace(self, old, new, extras):
        raise HTTPError(501, "Replace is currently no applicable")


class SNFBackend(MixinBackend, ActionBackend):

    pass


class ComputeBackend(MyBackend):
    '''
    Backend for Cyclades/Openstack compute instances
    '''

    def create(self, entity, extras):
        # Creating new compute instance
        try:

            snf_network = extras['snf_network']
            snf = extras['client']

            for mixin in entity.mixins:
                print mixin
                if 'occi.core.id' in mixin.attributes:
                    if mixin.related[0].term == 'os_tpl':
                        image_id = mixin.attributes['occi.core.id']
                    elif mixin.related[0].term == 'resource_tpl':
                        flavor = mixin
                        flavor_id = mixin.attributes['occi.core.id']


            vm_name = entity.attributes['occi.core.title']

            user_data = None
            user_pub_key = None
            meta_json = None
            personality = []

            if entity.attributes.has_key('org.openstack.compute.user_data'):
                            user_data = b64decode(entity.attributes['org.openstack.compute.user_data'])
                            # user_data = entity.attributes['org.openstack.compute.user_data']


            if entity.attributes.has_key('org.openstack.credentials.publickey.data'):
                            user_pub_key = entity.attributes['org.openstack.credentials.publickey.data']

           # Implementation for the meta.json file to use the respective NoCloud cloudinit driver
           # if user_data and user_pub_key:
           #     meta_json = json.dumps({'dsmode':'net','public-keys':user_pub_key,'user-data': user_data}, sort_keys=True,indent=4, separators=(',', ': ') )
           # elif user_data:
            #    meta_json = json.dumps({'dsmode':'net','user-data': user_data}, sort_keys=True,indent=4, separators=(',', ': ') )
           # elif user_pub_key:
            #    meta_json = json.dumps({'dsmode':'net','public-keys':user_pub_key}, sort_keys=True,indent=4, separators=(',', ': ') )

          #  if meta_json:
           #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!! CONTEXTUALIZATION!!!!!!!!!!!!!!!!!!!!!!"
           #     personality.append({'contents':b64encode(meta_json),
            #                            'path':' /var/lib/cloud/seed/config_drive/meta.js'})
            #    info = snf.create_server(vm_name, flavor_id, image_id,personality=personality)
           # else:
            #    info = snf.create_server(vm_name, flavor_id, image_id)

            if user_data:
                #userDataDict = dict([('user-data', user_data)])
                #userData = yaml.dump(userDataDict)
                userData = user_data
            if user_pub_key:
                pub_keyDict = dict([('public-keys',user_pub_key)])
                pub_key = yaml.dump(pub_keyDict)

        # kwargs = dict(project_id='6d9ec935-fcd4-4ae1-a3a0-10e612c4f867')
            kwargs = dict(project_id=extras.get('snf_project', None))

            if user_data and user_pub_key:
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!! CONTEXTUALIZATION - USER DATA & PUBLIC KEY!!!!!!!!!!!!!!!!!!!!!!"
                personality.append({'contents':b64encode(userData),
                                        'path':'/var/lib/cloud/seed/nocloud-net/user-data'})
                personality.append({'contents':b64encode(pub_key),
                                        'path':'/var/lib/cloud/seed/nocloud-net/meta-data'})
                info = snf.create_server(vm_name, flavor_id, image_id,personality=personality, **kwargs)
            elif user_data:
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!! CONTEXTUALIZATION - USER DATA!!!!!!!!!!!!!!!!!!!!!!"
                personality.append({'contents':b64encode(userData),
                                        'path':'/var/lib/cloud/seed/nocloud-net/user-data'})
                info = snf.create_server(vm_name, flavor_id, image_id,personality=personality, **kwargs)
            elif user_pub_key:
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!! CONTEXTUALIZATION - PUBLIC KEY!!!!!!!!!!!!!!!!!!!!!!"
                personality.append({'contents':b64encode(pub_key),
                                        'path':'/var/lib/cloud/seed/nocloud-net/meta-data'})
                for retries in range(2):
                    try:
                        info = snf.create_server(vm_name, flavor_id, image_id,personality=personality, **kwargs)
                    except ClientError as ce:
                        if ce.status in (409, ):
                            print 'ce, create an IP and retry'.format(ce=ce)
                            snf_network.create_floatingip(**kwargs)
                        else:
                            raise ce
            else:
                print 'Create a server with some attributes...'
                for retries in range(2):
                    try:
                        info = snf.create_server(vm_name, flavor_id, image_id, **kwargs)
                        break
                    except ClientError as ce:
                        if ce.status in (409, ):
                            print '{ce}, create an IP and retry'.format(ce=ce)
                            snf_network.create_floatingip(**kwargs)
                        else:
                            raise ce

            entity.attributes['occi.compute.state'] = 'inactive'
            entity.attributes['occi.core.id'] = str(info['id'])
            entity.attributes['occi.compute.architecture'] = SERVER_CONFIG['compute_arch']
            entity.attributes['occi.compute.cores'] = flavor.attributes['occi.compute.cores']
            entity.attributes['occi.compute.memory'] = flavor.attributes['occi.compute.memory']

            entity.actions = [
                infrastructure.STOP,
                infrastructure.SUSPEND,
                infrastructure.RESTART]

            # entity.attributes['occi.compute.hostname'] = SERVER_CONFIG['hostname'] % {'id':info['id']}
            info['adminPass']= ""
            print info
            networkIDs = info['addresses'].keys()
                #resource.attributes['occi.compute.hostname'] = SERVER_CONFIG['hostname'] % {'id':int(key)}
            if len(networkIDs)>0:    
                entity.attributes['occi.compute.hostname'] =  str(info['addresses'][networkIDs[0]][0]['addr'])
            else:
                entity.attributes['occi.compute.hostname'] = ""
               
        except (UnboundLocalError, KeyError) as e:
            raise HTTPError(406, 'Missing details about compute instance')

            

    def retrieve(self, entity, extras):
        
        #Triggering cyclades to retrieve up to date information

        snf = extras['snf']

        vm_id = int(entity.attributes['occi.core.id'])
        vm_info = snf.get_server_details(vm_id)
        vm_state = vm_info['status']
        
        status_dict = {'ACTIVE' : 'active',
                       'STOPPED' : 'inactive',
                       'REBOOT' : 'inactive',
                       'ERROR' : 'inactive',
                       'BUILD' : 'inactive',
                       'DELETED' : 'inactive',
                       'UNKNOWN' : 'inactive'
                       }
        
        entity.attributes['occi.compute.state'] = status_dict[vm_state]
                
        if vm_state == 'ERROR':
            raise HTTPError(500, 'ERROR building the compute instance')

        else:
            if entity.attributes['occi.compute.state'] == 'inactive':
                entity.actions = [infrastructure.START]
            if entity.attributes['occi.compute.state'] == 'active': 
                entity.actions = [infrastructure.STOP, infrastructure.SUSPEND, infrastructure.RESTART]


    def delete(self, entity, extras):

        #Deleting compute instance
        snf = extras['snf']
        vm_id = int(entity.attributes['occi.core.id'])
        snf.delete_server(vm_id)
        print "Deleting VM" + str(vm_id)


    def get_vm_actions(self, entity ,vm_state):
        
        actions = []
        
        status_dict = {'ACTIVE' : 'active',
                       'STOPPED' : 'inactive',
                       'REBOOT' : 'inactive',
                       'ERROR' : 'inactive',
                       'BUILD' : 'inactive',
                       'DELETED' : 'inactive',
                       'UNKNOWN' : 'inactive'
                       }

        if vm_state in status_dict:
            
            entity.attributes['occi.compute.state'] = status_dict[vm_state]
            if vm_state == 'ACTIVE':
                actions.append(infrastructure.STOP)
                actions.append(infrastructure.RESTART)
            elif vm_state in ('STOPPED'):
                actions.append(infrastructure.START)
                
            return actions
        else:
            raise HTTPError(500, 'Undefined status of the VM')

    def action(self, entity, action, attributes, extras):

        #Triggering action to compute instances

        client = extras['client']
        snf = extras['snf']

        vm_id = int(entity.attributes['occi.core.id'])
        vm_info = snf.get_server_details(vm_id)
        vm_state = vm_info['status']
        
        # Define the allowed actions depending on the state of the VM
        entity.actions = self.get_vm_actions(entity,vm_state)
        

        if vm_state == 'ERROR':
            raise HTTPError(500, 'ERROR building the compute instance')

        else:
            if action not in entity.actions:
                raise AttributeError("This action is currently no applicable in the current status of the VM (CURRENT_STATE = " + str(vm_state)+ ").")
            
            elif action == infrastructure.START:
                print "Starting VM" + str(vm_id)
                client.start_server(vm_id)
                
            elif action == infrastructure.STOP:
                print "Stopping VM"  + str(vm_id)
                client.shutdown_server(vm_id)
    
            elif action == infrastructure.RESTART:
                print "Restarting VM" + str(vm_id)
                snf.reboot_server(vm_id)

            elif action == infrastructure.SUSPEND:
                raise HTTPError(501, "This actions is currently no applicable")
