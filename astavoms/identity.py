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

from kamaki.clients import Client


class IdentityClient(Client):
    """An Extended Identity Client"""

    def list_users(self):
        """List all users"""
        return self.get('users', success=200).json['users']

    def create_user(
            self, username, first_name, last_name, affiliation,
            metadata=None):
        """Create a new user"""
        kwargs = dict(
            username=username,
            first_name=first_name,
            last_name=last_name,
            affilication=affiliation)
        if metadata:
            kwargs['metadata'] = metadata
        # Success should be 201, but server is currently returning 200, so...
        r = self.post('users', json=dict(user=kwargs), success=(200, 201))
        return r.json['user']

    def get_user_details(self, user_id):
        """Get user details"""
        return self.get('users/%s' % user_id, success=200).json['user']

    def modify_user(
            self, user_id,
            username=None,
            first_name=None,
            last_name=None,
            affilication=None,
            password=None,
            email=None,
            metadata=None):
        """Modify User"""
        kwargs = dict()
        if username is not None:
            kwargs['username'] = username
        if first_name is not None:
            kwargs['first_name'] = first_name
        if last_name is not None:
            kwargs['last_name'] = last_name
        if affilication is not None:
            kwargs['affilication'] = affilication
        if password is not None:
            kwargs['password'] = password
        if email is not None:
            kwargs['email'] = email
        if metadata is not None:
            kwargs['metadata'] = metadata
        r = self.put('users/%s' % user_id, json=dict(user=kwargs), success=200)
        return r.json['user']

    def activate_user(self, user_id):
        """Activate a user"""
        r = self.post(
            'users/%s/action' % user_id, json=dict(activate={}), success=200)
        return r.json['user']

    def deactivate_user(self, user_id):
        """Deactivate a user"""
        r = self.post(
            'users/%s/action' % user_id, json=dict(deactivate={}), success=200)
        return r.json['user']

    def renew_user_token(self, user_id):
        """Renew user authentication token"""
        r = self.post(
            'users/%s/action' % user_id, json=dict(renewToken={}), success=200)
        return r.json['user']
