# Copyright (C) 2012-2015 GRNET S.A.
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

from occi.backend import ActionBackend, KindBackend, MixinBackend
from occi.exceptions import HTTPError


# Network Backend for snf-occi-server


class NetworkBackend(KindBackend, ActionBackend):
    def create(self, entity, extras):
        raise HTTPError(501, "Currently not supported.")

    def action(self, entity, action, attributes, extras):
        raise HTTPError(501, "Currently not supported.")


class IpNetworkBackend(MixinBackend):
    def create(self, entity, extras):
        raise HTTPError(501, "Currently not supported.")


class IpNetworkInterfaceBackend(MixinBackend):
    """Ip Network Interface Backend"""


class NetworkInterfaceBackend(KindBackend):

    def create(self, entity, extras):
        raise HTTPError(501, "Currently not supported.")

    def action(self, entity, action, attributes, extras):
        raise HTTPError(501, "Currently not supported.")

    def update(self, old, new, extras):
        raise HTTPError(501, "Currently not supported.")

    def replace(self, old, new, extras):
        raise HTTPError(501, "Currently not supported.")
