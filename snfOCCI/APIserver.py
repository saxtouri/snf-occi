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

import uuid

from snfOCCI.registry import snfRegistry
from snfOCCI.compute import ComputeBackend, SNFBackend
from snfOCCI import config
from snfOCCI.config import VOMS_CONFIG, KEYSTONE_URL
from snfOCCI.network import (
    NetworkBackend, IpNetworkBackend, IpNetworkInterfaceBackend,
    NetworkInterfaceBackend)
from kamaki.clients.cyclades import CycladesNetworkClient
from snfOCCI.extensions import snf_addons

from kamaki.clients.cyclades import CycladesComputeClient as ComputeClient
from kamaki.clients.cyclades import CycladesClient
from kamaki.clients import astakos
from kamaki.clients import ClientError

from occi.core_model import Mixin, Resource
from occi.backend import MixinBackend
from occi.extensions.infrastructure import (
    COMPUTE, START, STOP, SUSPEND, RESTART, RESOURCE_TEMPLATE, OS_TEMPLATE,
    NETWORK, IPNETWORK, NETWORKINTERFACE, IPNETWORKINTERFACE)
from occi import wsgi
from occi.exceptions import HTTPError
from occi import core_model

from wsgiref.validate import validator
from webob import Request


class MyAPP(wsgi.Application):
    """An OCCI WSGI application"""

    def __init__(self):
        """Initialization of the WSGI OCCI application for synnefo"""
        global ENABLE_VOMS, VOMS_DB
        ENABLE_VOMS = VOMS_CONFIG['enable_voms']
        super(MyAPP, self).__init__(registry=snfRegistry())
        self._register_backends()
        VALIDATOR_APP = validator(self)

    def _register_backends(self):
        print "Register Backends"
        COMPUTE_BACKEND = ComputeBackend()
        NETWORK_BACKEND = NetworkBackend()
        NETWORKINTERFACE_BACKEND = NetworkInterfaceBackend()
        IPNETWORK_BACKEND = IpNetworkBackend()
        IPNETWORKINTERFACE_BACKEND = IpNetworkInterfaceBackend()

        self.register_backend(COMPUTE, COMPUTE_BACKEND)
        self.register_backend(START, COMPUTE_BACKEND)
        self.register_backend(STOP, COMPUTE_BACKEND)
        self.register_backend(RESTART, COMPUTE_BACKEND)
        self.register_backend(SUSPEND, COMPUTE_BACKEND)
        self.register_backend(RESOURCE_TEMPLATE, MixinBackend())
        self.register_backend(OS_TEMPLATE, MixinBackend())

        # Network related backends
        self.register_backend(NETWORK, NETWORK_BACKEND)
        self.register_backend(IPNETWORK, IPNETWORK_BACKEND)
        self.register_backend(NETWORKINTERFACE, NETWORKINTERFACE_BACKEND)
        self.register_backend(IPNETWORKINTERFACE, IPNETWORKINTERFACE_BACKEND)
        self.register_backend(snf_addons.SNF_USER_DATA_EXT, SNFBackend())
        self.register_backend(snf_addons.SNF_KEY_PAIR_EXT,  SNFBackend())

    def refresh_images(self, snf, client):
        print "Refresh images"
        try:
            images = snf.list_images()
            for image in images:
                IMAGE_ATTRIBUTES = {'occi.core.id': str(image['id'])}
                IMAGE = Mixin(
                    "http://schemas.ogf.org/occi/os_tpl#",
                    occify_terms(str(image['name'])),
                    [OS_TEMPLATE],
                    title='IMAGE', attributes=IMAGE_ATTRIBUTES)
                self.register_backend(IMAGE, MixinBackend())
        except:
            raise HTTPError(404, "Unauthorized access")

    def refresh_flavors(self, snf, client):
        print "Refresh flavors"
        flavors = snf.list_flavors(detail=True)
        for flavor in flavors:
            FLAVOR_ATTRIBUTES = {
                'occi.core.id': flavor['id'],
                'occi.compute.cores': str(flavor['vcpus']),
                'occi.compute.memory': str(flavor['ram']),
                'occi.storage.size': str(flavor['disk']),
            }
            FLAVOR = Mixin(
                "http://schemas.ogf.org/occi/resource_tpl#",
                occify_terms(str(flavor['name'])),
                [RESOURCE_TEMPLATE],
                title='FLAVOR', attributes=FLAVOR_ATTRIBUTES)
            self.register_backend(FLAVOR, MixinBackend())

    def refresh_network_instances(self, client):
        print "Refresh Networks"
        network_details = client.list_networks(detail=True)
        resources = self.registry.resources
        occi_keys = resources.keys()

        for network in network_details:
            if '/network/'+str(network['id']) not in occi_keys:
                netID = '/network/'+str(network['id'])
                snf_net = core_model.Resource(netID, NETWORK, [IPNETWORK])
                snf_net.attributes['occi.core.id'] = str(network['id'])

                # This info comes from the network details
                snf_net.attributes['occi.network.state'] = str(
                    network['status'])
                snf_net.attributes['occi.network.gateway'] = ''
                _is_public = 'True' if network['public'] is True else 'False'
                snf_net.attributes[
                    'occi.network.type'] = "Public = {0}".format(_is_public)
                self.registry.add_resource(netID, snf_net, None)

    def refresh_compute_instances(self, snf, client):
        """Syncing registry with cyclades resources"""
        print "Refresh Compute Instances (VMs)"

        servers = snf.list_servers()
        snf_keys = []
        for server in servers:
            snf_keys.append(str(server['id']))

        resources = self.registry.resources
        occi_keys = resources.keys()

        print 'OCCI keys: {0}'.format(occi_keys)
        for serverID in occi_keys:
            if '/compute/' in serverID and resources[serverID].attributes[
                    'occi.compute.hostname'] == "":
                self.registry.delete_resource(serverID, None)
        occi_keys = resources.keys()

        # Compute instances in synnefo not available in registry
        diff = [x for x in snf_keys if '/compute/'+x not in occi_keys]
        for key in diff:
            details = snf.get_server_details(int(key))
            flavor = snf.get_flavor_details(details['flavor']['id'])
            try:
                print "Get image of flavor {flavor}, VM {vm}".format(
                    flavor=details['flavor']['id'], vm=key)
                image = snf.get_image_details(details['image']['id'])
                for i in self.registry.backends:
                    if i.term == occify_terms(str(image['name'])):
                        rel_image = i
                    if i.term == occify_terms(str(flavor['name'])):
                        rel_flavor = i

                resource = Resource(key, COMPUTE, [rel_flavor, rel_image])
                resource.actions = [START]
                resource.attributes['occi.core.id'] = key
                resource.attributes['occi.compute.state'] = 'inactive'
                resource.attributes['occi.compute.architecture'] = (
                    config.COMPUTE['arch'])
                resource.attributes['occi.compute.cores'] = str(
                    flavor['vcpus'])
                resource.attributes['occi.compute.memory'] = str(flavor['ram'])
                resource.attributes['occi.core.title'] = str(details['name'])
                networkIDs = details['addresses'].keys()
                if len(networkIDs) > 0:
                    resource.attributes['occi.compute.hostname'] = str(
                        details['addresses'][networkIDs[0]][0]['addr'])
                else:
                    resource.attributes['occi.compute.hostname'] = ""
                self.registry.add_resource(key, resource, None)

                link_id = str(uuid.uuid4())
                net_str = (
                    "http://schemas.ogf.org/occi/infrastructure#"
                    "networkinterface{0}".format(link_id))
                for netKey in networkIDs:
                    NET_LINK = core_model.Link(
                        net_str,
                        NETWORKINTERFACE, [IPNETWORKINTERFACE], resource,
                        self.registry.resources['/network/'+str(netKey)])

                    for version in details['addresses'][netKey]:
                        ip4address = ''
                        ip6address = ''
                        if version['version'] == 4:
                            ip4address = str(version['addr'])
                            allocheme = str(version['OS-EXT-IPS:type'])
                        elif version['version'] == 6:
                            ip6address = str(version['addr'])
                        allocheme = str(version['OS-EXT-IPS:type'])

                    if 'attachments' in details.keys():
                        for item in details['attachments']:
                            NET_LINK.attributes = {
                                'occi.core.id': link_id,
                                'occi.networkinterface.allocation': allocheme,
                                'occi.networking.interface': str(item['id']),
                                'occi.networkinterface.mac': str(
                                    item['mac_address']),
                                'occi.networkinterface.address': ip4address,
                                'occi.networkinterface.ip6':  ip6address}
                    elif len(details['addresses'][netKey]) > 0:
                        NET_LINK.attributes = {
                            'occi.core.id': link_id,
                            'occi.networkinterface.allocation': allocheme,
                            'occi.networking.interface': '',
                            'occi.networkinterface.mac': '',
                            'occi.networkinterface.address': ip4address,
                            'occi.networkinterface.ip6':  ip6address}
                    else:
                        NET_LINK.attributes = {
                            'occi.core.id': link_id,
                            'occi.networkinterface.allocation': '',
                            'occi.networking.interface': '',
                            'occi.networkinterface.mac': '',
                            'occi.networkinterface.address': '',
                            'occi.networkinterface.ip6': ''}
                    resource.links.append(NET_LINK)
                    self.registry.add_resource(link_id, NET_LINK, None)
            except ClientError as ce:
                print ce.status
                if ce.status == 404 or ce.status == 500:
                    print('Image not found, sorry!!!')
                    continue
                else:
                    raise ce

        # Compute instances in registry not available in synnefo
        diff = [x for x in occi_keys if x[9:] not in snf_keys]
        for key in diff:
            if '/network/' not in key:
                self.registry.delete_resource(key, None)

    def __call__(self, environ, response):
        """Enable VOMS Authorization"""
        print "SNF_OCCI application has been called"
        req = Request(environ)

        if 'HTTP_X_AUTH_TOKEN' not in req.environ:
            # Redirect caller to Keystone URL to get a token
            print "An authentication token has NOT been provided!"
            status = '401 Not Authorized'
            headers = [
                ('Content-Type', 'text/html'),
                (
                    'Www-Authenticate',
                    'Keystone uri=\'{0}\''.format(KEYSTONE_URL))]
            response(status, headers)
            print '401 - give caller this URL: {0}'.format(KEYSTONE_URL)
            return [str(response)]

        print 'An authentication token has been provided'
        environ['HTTP_AUTH_TOKEN'] = req.environ['HTTP_X_AUTH_TOKEN']
        try:
            print "Get project"
            snf_project = req.environ['HTTP_X_SNF_PROJECT']
        except KeyError:
            print "No project provided, go to plan B"
            astakosClient = astakos.AstakosClient(
                config.KAMAKI['astakos_url'], environ['HTTP_AUTH_TOKEN'])
            projects = astakosClient.get_projects()
            user_info = astakosClient.authenticate()
            user_uuid = user_info['access']['user']['id']
            snf_project = '6d9ec935-fcd4-4ae1-a3a0-10e612c4f867'
            for project in projects:
                if project['id'] != user_uuid:
                    snf_project = project['id']
                    print "Project found"
                    break
        if ENABLE_VOMS:
            compClient = ComputeClient(
                config.KAMAKI['compute_url'], environ['HTTP_AUTH_TOKEN'])
            cyclClient = CycladesClient(
                config.KAMAKI['compute_url'], environ['HTTP_AUTH_TOKEN'])
            netClient = CycladesNetworkClient(
                config.KAMAKI['network_url'], environ['HTTP_AUTH_TOKEN'])
            try:
                # Up-to-date flavors and images
                self.refresh_images(compClient, cyclClient)
                self.refresh_flavors(compClient, cyclClient)
                self.refresh_network_instances(netClient)
                self.refresh_compute_instances(compClient, cyclClient)
                # token will be represented in self.extras
                return self._call_occi(
                    environ, response,
                    security=None, token=environ['HTTP_AUTH_TOKEN'],
                    snf=compClient, client=cyclClient,
                    snf_network=netClient, snf_project=snf_project)
            except HTTPError:
                print "Exception from unauthorized access!"
                status = '401 Not Authorized'
                headers = [
                    ('Content-Type', 'text/html'),
                    (
                        'Www-Authenticate',
                        'Keystone uri=\'{0}\''.format(KEYSTONE_URL))]
                response(status, headers)
            print '401 - give caller this URL: {0}'.format(KEYSTONE_URL)
            return [str(response)]
        else:
            print 'I have a token and a project, we can proceed'
            compClient = ComputeClient(
                config.KAMAKI['compute_url'], environ['HTTP_AUTH_TOKEN'])
            cyclClient = CycladesClient(
                config.KAMAKI['compute_url'], environ['HTTP_AUTH_TOKEN'])
            netClient = CycladesNetworkClient(
                config.KAMAKI['network_url'], environ['HTTP_AUTH_TOKEN'])

            # Up-to-date flavors and images
            self.refresh_images(compClient, cyclClient)

            self.refresh_flavors(compClient, cyclClient)
            self.refresh_network_instances(cyclClient)
            self.refresh_compute_instances(compClient, cyclClient)

            # token will be represented in self.extras
            return self._call_occi(
                environ, response,
                security=None, token=environ['HTTP_AUTH_TOKEN'],
                snf=compClient, client=cyclClient, snf_network=netClient,
                snf_project=snf_project)


def occify_terms(term):
    """:return: Occified term, compliant with GFD 185"""
    return term.strip().lower().replace(' ', '_').replace('.', '-').replace(
        '(', '_').replace(')', '_').replace('@', '_').replace('+', '-_')
