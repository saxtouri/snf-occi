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

if [ -z "$OS_TPL" ]; then echo "E: OS_TPL not set"; exit 1; fi;
echo "OS_TPL = ${OS_TPL}"

if [ -z "$RESOURCE_TPL" ]; then echo "E: RESOURCE_TPL not set"; exit 1; fi;
echo "RESOURCE_TPL = ${RESOURCE_TPL}";


if [ -z "$SNF_OCCI_DEBUG" ]; then
    XARGS="";
else 
    XARGS="-d";
fi;

echo "Vars OK, run tests"
echo


BASE_CMD="occi ${XARGS} --endpoint ${OCCI_ENDPOINT} ${AUTH}"
VM_INFO="/tmp/vm.info"

echo "Preparation ..."
echo "... create a server instance"
CMD="${BASE_CMD} --action create --resource compute "
CMD="${CMD} --attribute occi.core.title=\"OCCI test VM\""
CMD="${CMD} --mixin os_tpl#${OS_TPL} --mixin resource_tpl#${RESOURCE_TPL}"
echo "$CMD"
VM_URL=$(eval $CMD)
echo $VM_URL
VM_SUFFIX=(`echo ${VM_URL}|awk '{n=split($0,a,"/"); print "/"a[n-1]"/"a[n]}'`)

echo "... create a Volume"
CMD="${BASE_CMD} --action create --resource storage "
CMD="${CMD} --attribute occi.core.title=\"My test volume\""
CMD="${CMD} --attribute occi.storage.size=\"10\""
echo "$CMD"
VOLUME_URL=$(eval $CMD)
echo "${VOLUME_URL}"
VOLUME_ID=(`echo $VOLUME_URL|awk '{n=split($0,a,"/"); print a[n];}'`)

echo "... wait for server to boot"
CMD="${BASE_CMD} --action describe --resource ${VM_SUFFIX} > ${VM_INFO}";
echo "$CMD";
eval $CMD;
STATE=(`awk '/occi.compute.state/{n=split($0,a," = "); print a[2];}' ${VM_INFO}`)
WAIT=10;
while [ $STATE != 'active' ]
do
    echo "...server state is ${STATE}, wait ${WAIT}\""
    sleep $WAIT;
    let "WAIT++";
    eval $CMD;
    STATE=(`awk '/occi.compute.state/{n=split($0,a," = "); print a[2];}' ${VM_INFO}`);
done;
echo "...server state is ${STATE}"
echo
echo

echo "Attach volume to server"
CMD="${BASE_CMD} --action link --resource ${VM_SUFFIX} \
    --link /storage/${VOLUME_ID}"
echo $CMD
LINK=$(eval $CMD)
LINK_SUFFIX=(`echo ${LINK}|awk '{n=split($0,a,"/"); print "/"a[n-1]"/"a[n]}'`)
echo

printf "The volume is being attached  "
for i in `seq 1 10`; do
    sleep 1
    printf "\b/"
    sleep 1
    printf "\b-"
    sleep 1
    printf "\b\\"
    sleep 1
    printf "\b|"
done
echo
echo

echo "Information on this particular storage link"
echo "Meaning: kamaki volume info ${VOLUME_ID}"
CMD="${BASE_CMD} --action describe --resource ${LINK_SUFFIX}"
echo "$CMD"
eval $CMD
echo
echo

echo "Detach volume from server"
CMD="${BASE_CMD} --action unlink --resource ${LINK_SUFFIX}"
echo $CMD
eval $CMD
echo

printf "The volume is being detached  "
for i in `seq 1 10`; do
    sleep 1
    printf "\b/"
    sleep 1
    printf "\b-"
    sleep 1
    printf "\b\\"
    sleep 1
    printf "\b|"
done
echo
echo

echo "... clean up"
CMD="${BASE_CMD} --action delete --resource ${VM_SUFFIX}";
echo $CMD
eval $CMD
CMD="${BASE_CMD} --action delete --resource /storage/${VOLUME_ID}"
echo $CMD
eval $CMD
CMD="rm -f ${VM_INFO}"
echo $CMD
eval $CMD
echo
