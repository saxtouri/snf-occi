#!/bin/bash
# Copyright (C) 2017 GRNET S.A.
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

echo "Check vars ..."

if [ -z "$OCCI_ENDPOINT" ]; then echo "E: OCCI_ENDPOINT not set"; exit 1; fi;
echo "OCCI_ENDPOINT = ${OCCI_ENDPOINT}"

if [ -z "$TOKEN" ]; then echo "E: TOKEN not set"; exit 1; fi;
echo "TOKEN = ${TOKEN}"

echo "Vars OK, run tests"
echo

if [ -z "$SNF_OCCI_DEBUG" ]; then
    XARGS="-s";
else 
    XARGS="-v";
fi

BASE_CMD="curl ${XARGS} -H'X-Auth-Token: ${TOKEN}'"


echo "Create a (private) network"
echo "Equivalent: kamaki netwotk create --name \"My Test Network\" \\"
CMD="${BASE_CMD} -X'POST' $OCCI_ENDPOINT/network/ \
    -H 'Category: network; \
        scheme=\"http://schemas.ogf.org/occi/infrastructure#\"; \
        class=\"kind\",ipnetwork; \
        scheme=\"http://schemas.ogf.org/occi/infrastructure/network#\"; \
        class=\"mixin\" '
    -H 'X-OCCI-Attribute: occi.core.title=\"My Test Network\", \
        occi.network.address=\"192.168.0.0/24\"'"
echo $CMD
NETWORK_URL=$(eval $CMD)
echo ${NETWORK_URL}
NETWORK_ID=(`echo $NETWORK_URL|awk -F/ '{print $NF;}'`)
echo
echo


echo "Retrieve network information"
echo "Equivalent: kamaki network info ${NETWORK_ID}"
CMD="${BASE_CMD} $OCCI_ENDPOINT/network/${NETWORK_ID}"
echo $CMD
eval $CMD
echo
echo

echo "Retrieve network information"
echo "Equivalent: kamaki network list"
CMD="${BASE_CMD} $OCCI_ENDPOINT/network"
echo $CMD
eval $CMD
echo
echo

echo "Delete network"
echo "Equivalent: kamaki network delete ${NETWORK_ID}"
CMD="${BASE_CMD} -X'DELETE' $OCCI_ENDPOINT/network/${NETWORK_ID}"
echo $CMD
eval $CMD
echo
echo
