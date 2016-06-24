from kamaki.clients.compute import ComputeClient
from kamaki.clients.cyclades import CycladesClient
from kamaki.cli.config  import Config

from occi import registry
from occi.core_model import Mixin
from occi.backend import MixinBackend
from occi.extensions.infrastructure import RESOURCE_TEMPLATE, OS_TEMPLATE

class snfRegistry(registry.NonePersistentRegistry):

    def add_resource(self, key, resource, extras):

        key = resource.kind.location + resource.attributes['occi.core.id']
        resource.identifier = key

        super(snfRegistry, self).add_resource(key, resource, extras)

    def set_hostname(self, hostname):
	super(snfRegistry, self).set_hostname("https://okeanos-occi2.hellasgrid.gr:9000")
