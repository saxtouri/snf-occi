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

from occi import registry
from snfOCCI import config


class snfRegistry(registry.NonePersistentRegistry):

    def add_resource(self, key, resource, extras):

        key = resource.kind.location + resource.attributes['occi.core.id']
        resource.identifier = key

        super(snfRegistry, self).add_resource(key, resource, extras)

    def set_hostname(self, hostname):
        super(snfRegistry, self).set_hostname(config.HOSTNAME)
