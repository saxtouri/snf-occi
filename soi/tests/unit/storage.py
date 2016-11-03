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

from soi.tests import fakes
from soi import storage
from mock import patch


def test_openstackify_volumes_display_names():
    response_result = [{'display_name': 'boot volume', 'id': '5609', },
                       {'display_name': None, 'id': '67712'}]
    openstackified_result = [{'display_name': 'boot volume',
                              'displayName': 'boot volume', 'id': '5609'},
                             {'display_name': None, 'displayName': None,
                              'id': '67712'}]
    storage._openstackify_volumes_display_names(response_result)
    assert response_result == openstackified_result
