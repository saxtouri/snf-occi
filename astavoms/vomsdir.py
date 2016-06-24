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

import ldap
import ssl


class LDAPUser:
    """An LDAP manager for VOMS users"""

    def __init__(self, ldap_url, user, password, base_dn, ca_cert_file=None):
        """
        :raises ldap.LDAPError: if connection fails
        """
        self.con = ldap.initialize(ldap_url)
        self.base_dn = base_dn

        if ca_cert_file:
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, ca_cert_file)
            self.con.start_tls_s()

        self.user, self.password = user, password

    def __enter__(self):
            self.con.simple_bind_s(self.user, self.password)
            return self

    def __exit__(self, type, value, traceback):
            self.con.unbind()

    def _search(self, query, attrlist):
        return self.con.search_s(
            self.base_dn, ldap.SCOPE_SUBTREE, query, attrlist)

    def search_by_uid(self, userUID, attrlist=[]):
        """
        :return: (dict) of the form dict(dn={...})
        """
        query = '(&(objectclass=person)(uid=%s))' % userUID
        return dict(self._search(query, attrlist))

    def search_by_vo(self, user_cn, user_vo, attrlist=[]):
        """
        :return: (dict) of the form dict(dn={...})
        """
        query = '(&(objectclass=person)(cn=%s)(sn=%s))' % (user_cn, user_vo)
        return dict(self._search(query, attrlist))

    def search_by_token(self, token, attrlist=[]):
        """
        :return: (dict) of the form dict(dn={...})
        """
        query = '(&(objectclass=person)(userpassword=%s))' % token
        return dict(self._search(query, attrlist))

    def delete_user(self, userUID):
        """Remove a user from the LDAP directory
        :raises ldap.NO_SUCH_OBJECT: if this user is not in the LDAP directory
        """
        dn = 'uid=%s,%s' % (userUID, self.base_dn)
        self.con.delete_s(dn)

    def list_users(self, attrlist=[]):
        """
        :return: (dict) of the form dict(dn={...}, ...)
        """
        return dict(self._search('(&(objectclass=person))', attrlist))

    def create(
            self, userUID, certCN, email, token, user_vo, userClientDN,
            userCert=None):
        add_record = [
            ('objectclass', [
                'person', 'organizationalperson', 'inetorgperson', 'pkiuser']),
            ('uid', [userUID]),
            ('cn', [certCN]),
            ('sn', [user_vo]),
            ('userpassword', [token]),
            ('mail', [email]),
            ('givenname', userClientDN),
            ('ou', ['users'])
        ]
        dn = 'uid=%s,%s' % (userUID, self.base_dn)
        self.con.add_s(dn, add_record)

        if userCert:
            cert_der = ssl.PEM_cert_to_DER_cert(userCert)
            mod_attrs = [(ldap.MOD_ADD, 'userCertificate;binary', cert_der)]
            self.con.modify_s(dn, mod_attrs)

    def update_token(self, userUID, newToken):
        dn = 'uid=%s,%s' % (userUID, self.base_dn)
        mod_attrs = [(ldap.MOD_REPLACE, 'userpassword', newToken)]
        self.con.modify_s(dn, mod_attrs)
