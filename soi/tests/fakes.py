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


class FakeReq:
    """use it for testing"""
    def __init__(self, *args, **kwargs):
        self.environ = dict()

    def get_response(self, *args, **kwargs):
        """Don't do enything"""


class DummyClass:
    """use it for testing"""
    def app(self, *args, **kwargs):
        """inner app"""

    def get_from_response(self, *args, **kwargs):
        """Don't do enything"""
