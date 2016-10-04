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
"""
This it the entry point for paste deploy .

Paste config file needs to point to egg:<package name>:<entrypoint name>:

use = egg:snfOCCI#sample_app

sample_app entry point is defined in setup.py:

entry_points='''
[paste.app_factory]
sample_app = soi:main
''',

which point to this function call (<module name>:function).
"""

from soi import wsgi
from soi import synnefo

# W0613:unused args
# pylint: disable=W0613


# noinspection PyUnusedLocal
def main(global_config, **settings):
    """This is the entry point for paste into the OCCI OS world."""
    factory = wsgi.SNFOCCIMiddleware.factory({'openstack_version': 'v2.1'})
    return factory(synnefo.call_kamaki)
