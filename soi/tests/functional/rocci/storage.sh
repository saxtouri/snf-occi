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

AUTH=""
if [ -z "$USER_PROXY" ]; then
    echo "W: USER_PROXY not set";
    if [ -z "$TOKEN" ]; then
        echo "E: TOKEN not set";
        exit 1;
    else
        echo "TOKEN = ${TOKEN}";
        AUTH="-n token --token ${TOKEN}"
    fi;
else
    echo "USER_PROXY = ${USER_PROXY}"
    AUTH="-n x509 -X --user-cred ${USER_PROXY}"
fi;


if [ -z "$SNF_OCCI_DEBUG" ]; then
    XARGS="";
else 
    XARGS="-d";
fi;

echo "Vars OK, run tests"
echo


BASE_CMD="occi ${XARGS} --endpoint ${OCCI_ENDPOINT} ${AUTH}"

echo "Create a Volume"
echo "Meaning: kamaki volume create --name \"My test volume\" \\"
echo "    --size 10 --volume-type 2"
CMD="${BASE_CMD} --action create --resource storage "
CMD="${CMD} --attribute occi.core.title=\"My test volume\""
CMD="${CMD} --attribute occi.storage.size=\"10\""
echo "$CMD"
VOLUME_URL=$(eval $CMD)
echo "${VM_URL}"
VOLUME_ID=(`echo $VOLUME_URL|awk '{n=split($0,a,"/"); print a[n];}'`)
echo
echo

echo "List Volumes"
echo "Meaning: kamaki volume list"
CMD="${BASE_CMD} --action list --resource storage"
echo "$CMD"
eval $CMD
echo
echo

echo "Details on a Volume"
echo "Meaning: kamaki volume info ${VOLUME_ID}"
CMD="${BASE_CMD} --action describe --resource /storage/${VOLUME_ID}"
echo "$CMD"
eval $CMD
echo
echo


echo "Clean up"
CMD="${BASE_CMD} --action delete --resource /storage/${VOLUME_ID}"
echo $CMD
eval $CMD
echo
echo
