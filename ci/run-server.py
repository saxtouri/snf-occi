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

from paste import deploy
import logging
from paste import httpserver

try:
    from soi.config import PASTE_INI, HOST, PORT
except (ImportError, NameError) as err:
    from sys import stderr, exit
    stderr.write('{err}\n'.format(err=err))
    stderr.write(
        'Make sure soi/config.py exists and contains appropriate values.\n')
    stderr.write('Refer to the documentation for more information\n')
    exit(1)

LOG = logging.getLogger(__name__)

# Setup a server for testing
application = deploy.loadapp('config:{0}'.format(PASTE_INI))
httpserver.serve(application, HOST, PORT)
