#!/bin/bash
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


echo "Create a volume"
echo "Meaning: kamaki volume create --name \"My Test Volume\" \\"
echo "    --size 10 --volume-type 2"
CMD="${BASE_CMD} -X'POST' $OCCI_ENDPOINT/storage/ \
    -H 'Category: storage; \
        scheme=\"http://schemas.ogf.org/occi/infrastructure#\"; \
        class=\"kind\"' \
    -H 'X-OCCI-Attribute: occi.core.title=\"My Test Volume\"'
    -H 'X-OCCI-Attribute: occi.storage.size=10'"
echo $CMD
VOLUME_URL=$(eval $CMD)
echo ${VOLUME_URL}
VOLUME_ID=(`echo $VOLUME_URL|awk '{n=split($0,a,"/"); print a[n];}'`)
echo
echo

echo "List volumes"
echo "Meaning: kamaki volume list"
CMD="${BASE_CMD} $OCCI_ENDPOINT/storage/"
echo "$CMD"
eval $CMD
echo
echo

echo "Get volume information"
echo "Meaning: kamaki volume info ${VOLUME_ID}"
CMD="${BASE_CMD} $OCCI_ENDPOINT/storage/${VOLUME_ID}"
echo "$CMD"
eval $CMD
echo
echo

echo "Delete a volume"
echo "Meaning: kamaki volume delete ${VOLUME_ID}"
CMD="${BASE_CMD} -X'DELETE' $OCCI_ENDPOINT/storage/${VOLUME_ID}"
echo "$CMD"
eval $CMD
echo
echo
