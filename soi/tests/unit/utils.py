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

from soi import utils, config
from mock import patch
from soi.tests import fakes
import webob.exc
from nose.tools import assert_raises


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


@patch('soi.tests.fakes.DummyClass.get_from_response', return_value='g f r')
@patch('soi.tests.fakes.FakeReq.get_response', return_value='my response')
def test_empty_list_200(gr, gfr):
    """Test the empty list method"""
    cls, req = fakes.DummyClass(), fakes.FakeReq()
    r = utils.empty_list_200(cls, req)
    assert r == 'g f r'
    gfr.assert_called_once_with('my response', 'empty list', [])
    gr.assert_called_once_with(cls.app)


def test_check_activation():
    """Test check activation method"""

    @utils.check_activation
    def DummyMethod():
        pass

    func_full_name = DummyMethod.__module__ + '.' + DummyMethod.__name__
    DISABLED_METHODS = (func_full_name,)
    setattr(config, 'DISABLED_METHODS', DISABLED_METHODS)

    assert_raises(webob.exc.HTTPNotImplemented, DummyMethod)
