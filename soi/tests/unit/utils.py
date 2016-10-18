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

from soi import utils
from mock import patch


def test_patch_class_methods():
    """Test utils.patch_class_methods"""
    class DummyClass:
        """use it for testing"""
        def a_method(self, an_arg):
            """a method"""

        def an_other_method(self, an_arg, antoher_arg):
            """a method"""

    function_map = {
        'a_method': lambda self, x: 'replace {0}'.format(x),
        'an_other_method': lambda self, x, y: 'replace {0} {1}'.format(x, y),
    }

    utils.patch_class_methods(DummyClass, function_map)
    client = DummyClass()

    assert client.a_method('arg1') == 'replace arg1'
    assert client.an_other_method('arg1', 'arg2') == 'replace arg1 arg2'


def test_empty_list_200():
    """Test the empty list method"""
    class FakeReq:
        """use it for testing"""
        environ = dict()

        def get_response(self, *args, **kwargs):
            """Don't do enything"""

    class DummyClass:
        """use it for testing"""
        def app(self, *args, **kwargs):
            """inner app"""

        def get_from_response(self, *args, **kwargs):
            """Don't do enything"""

    setattr(utils, 'FakeReq', FakeReq)
    setattr(utils, 'DummyClass', DummyClass)

    with patch(
            'soi.utils.FakeReq.get_response',
            return_value='my response') as gr:
        with patch(
                'soi.utils.DummyClass.get_from_response',
                return_value='get from response') as gfr:
            cls, req = DummyClass(), FakeReq()
            r = utils.empty_list_200(cls, req)
            assert r == 'get from response'
            gfr.assert_called_once_with('my response', 'empty list', [])
            gr.assert_called_once_with(cls.app)
