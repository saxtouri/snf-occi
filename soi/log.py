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

from functools import wraps


def _reavealer(f, logstr, *args, **kwargs):
    """Reveal when a method is called and finished"""
    print "---> {0}".format(logstr)
    try:
        r = f(*args, **kwargs)
    except Exception as e:
        print '-X- {0}: {1}'.format(logstr, e)
        raise
    print "<--- {0}".format(logstr)
    return r


def reveale_me(f):
    """Reveal stand alone methods"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        logstr = "{me}".format(me=f.__name__)
        return _reavealer(f, logstr, *args, **kwargs)
    return wrapper


def reveale_cme(f):
    """reveal class member methods"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        logstr = "{self}.{me}".format(self=args[0], me=f.__name__)
        return _reavealer(f, logstr, *args, **kwargs)
    return wrapper
