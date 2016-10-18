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
# along with this program. If not, see <http://www.gnu.org/licenses/>

#  Copy this file as config.py and fill in the appropriate values

import os

AUTH_URL = os.environ.get('AUTH_URL')
CA_CERTS = os.environ.get('CA_CERTS', '/etc/ssl/certs/ca-certificates.crt')
KEYSTONE_URL = os.environ.get('KEYSTONE_URL')

HOST = os.environ.get('HOST', '127.0.0.1')
PORT = os.environ.get('PORT', '8080')
PASTE_INI = '/snf-occi/ci/soi.ini'
