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

from soi import synnefo
from mock import patch
from json import dumps


def test__coerce_json_values():
    """Change value types of specific json keys.
    At present implementation, convert all ids from int
    to string, in order to satisfy openstack compatibility.
    """
    examples = (
        # Tests without keys in need of conversion:
        (  # Simple case, trouble free
            {'a': 'a', 'b': ['a', 'b'], 'c': {'a': 'a', 'b': 'b'}},
            {'a': 'a', 'b': ['a', 'b'], 'c': {'a': 'a', 'b': 'b'}},
        ),
        (  # Numbers as values and 1 level nesting
            {'a': 1, 'b': [1, 'b'], 'c': {'a': 'a', 'b': 2}},
            {'a': 1, 'b': [1, 'b'], 'c': {'a': 'a', 'b': 2}},
        ),
        (  # Numbers as keys must stay unchanged
            {1: 'a', 'b': [1, 'b'], 3: {1: 'a', 'b': 2}},
            {1: 'a', 'b': [1, 'b'], 3: {1: 'a', 'b': 2}},
        ),
        (  # 2-level nesting
            {
                'a': 1,
                'b': [{1: 1, 2: '2'}, 'b'],
                'c': {'a': 'a', 'b': [1, '2', 'c']}},
            {
                'a': 1,
                'b': [{1: 1, 2: '2'}, 'b'],
                'c': {'a': 'a', 'b': [1, '2', 'c']}},
        ),
        # Tests with keys in need of conversion:
        (  # Simple case, trouble free
            {'id': 'a', 'volume_id': ['a', 'b'], 'serverId': {'volumeId': 'a', 'b': 'b'}},
            {'id': 'a', 'volume_id': ['a', 'b'], 'serverId': {'volumeId': 'a', 'b': 'b'}},
        ),
        (  # Numbers as values and 1 level nesting
            {'id':  1 , 'id': [1, 'b'], 'id': {'a': 'a', 'id':  2 }},
            {'id': '1', 'id': [1, 'b'], 'id': {'a': 'a', 'id': '2'}},
        ),
        (  # 2-level nesting
            {
                'id': 1,
                'id': [{1: 1, 2: '2'}, 'b'],
                'c': {'a': 'a', 'id': [1, '2', 'c', { 'id':  1 }]}},
            {
                'id': '1',
                'id': [{1: 1, 2: '2'}, 'b'],
                'c': {'a': 'a', 'id': [1, '2', 'c', { 'id': '1'}]}},
        )
    )

    for input_, output_ in examples:
        r = synnefo._coerce_json_values(input_)
        assert r == output_


class DummyResponse:
    status_code = 1000
    status = 'status'
    headers = {
        'content-length': '10', 'content-type': 'application/json'}
    json = {"a": "b"}
    content = dumps(json)


def my_method(cls, *args, **kwargs):
    """dummy method"""
    return DummyResponse()


def start_response(*args, **kwargs):
    """dummy method"""
synnefo.start_response = start_response
synnefo.CycladesNetworkClient.my_method = my_method
synnefo.CycladesComputeClient.my_method = my_method


@patch('soi.synnefo.start_response')
def test_call_kamaki_compute(start_response):
    """This is the Synnefo-end of the application"""
    environ = dict(
        method_name='my_method',
        service_type='compute',
        HTTP_X_AUTH_TOKEN='my-token')
    r = synnefo.call_kamaki(environ, start_response)
    assert r == DummyResponse.content


@patch('soi.synnefo.start_response')
def test_call_kamaki_compute_no_body(start_response):
    environ = dict(
        method_name='my_method',
        service_type='compute',
        HTTP_X_AUTH_TOKEN='my-token')
    DummyResponse.json = None
    DummyResponse.content = None
    r = synnefo.call_kamaki(environ, start_response)
    assert r == ''


@patch('soi.synnefo.start_response')
def test_call_kamaki_network(start_response):
    environ = dict(
        method_name='my_method',
        service_type='network',
        HTTP_X_AUTH_TOKEN='my-token')
    DummyResponse.json = {'b': 'c'}
    DummyResponse.content = dumps(DummyResponse.json)
    r = synnefo.call_kamaki(environ, start_response)
    assert r == DummyResponse.content
