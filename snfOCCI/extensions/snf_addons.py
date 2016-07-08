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

# Extensions for supporting contextualization in snf-occi
# The names are chosen so as to be compatible with rOCCI and fedcloud
# (see: https://wiki.egi.eu/wiki/Fedcloud-tf:WorkGroups:Contextualisation)

from occi import core_model


_SNF_USER_DATA_ATTRIBUTES = {'org.openstack.compute.user_data': ''}
SNF_USER_DATA_EXT = core_model.Mixin(
    'http://schemas.openstack.org/compute/instance#',
    'user_data', attributes=_SNF_USER_DATA_ATTRIBUTES)

_SNF_KEY_PAIR_ATTRIBUTES = {
    'org.openstack.credentials.publickey.name': '',
    'org.openstack.credentials.publickey.data': '', }
SNF_KEY_PAIR_EXT = core_model.Mixin(
    'http://schemas.openstack.org/instance/credentials#',
    'public_key', attributes=_SNF_KEY_PAIR_ATTRIBUTES)
