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

from setuptools import setup

setup(
    name='snf-occi',
    version='0.2',
    description='OCCI to Openstack/Cyclades API bridge',
    url='http://code.grnet.gr/projects/snf-occi',
    license='BSD',
    packages=[
        'snfOCCI', 'snfOCCI.snf_voms', 'snfOCCI.extensions', 'astavomaki'],
    entry_points='''
        [paste.app_factory]
        snf_occi_app = snfOCCI:main
        ''',
)
