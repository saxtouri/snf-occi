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

if [ -z "$OS_TPL" ]; then echo "E: OS_TPL not set"; exit 1; fi;
echo "OS_TPL = ${OS_TPL}"

if [ -z "$RESOURCE_TPL" ]; then echo "E: RESOURCE_TPL not set"; exit 1; fi;
echo "RESOURCE_TPL = ${RESOURCE_TPL}";

echo "Vars OK, run tests"
echo

if [ -z "$SNF_OCCI_DEBUG" ]; then
    XARGS="-s";
else 
    XARGS="-v";
fi

BASE_CMD="curl ${XARGS} -H'X-Auth-Token: ${TOKEN}'"
VM_INFO="/tmp/vm.info"

echo "List everything"
echo "Meaning: kamaki image list || kamaki flavor list || kamaki volume list" \
    "|| kamaki network list"
CMD="${BASE_CMD} $OCCI_ENDPOINT/-/"
echo "$CMD"
eval $CMD
echo
echo


echo "Create a server"
echo "Meaning: kamaki server create --name \"My Test VM\" \\"
echo "    --flavor-id ${RESOURCE_TPL} --image-id ${OS_TPL}"
CMD="${BASE_CMD} -X'POST' $OCCI_ENDPOINT/compute \
    -H'Category: compute; scheme=\"http://schemas.ogf.org/occi/infrastructure#\"; class=\"kind\"' \
    -H'Content-Type: text/occi' \
    -H'Category: ${RESOURCE_TPL}; scheme=\"http://schemas.openstack.org/template/resource#\"; class=\"mixin\"' \
    -H'Category: ${OS_TPL}; scheme=\"http://schemas.openstack.org/template/os#\"; class=\"mixin\"' \
    -H'X-OCCI-Attribute: occi.core.title=\"OCCI test VM\"'"
echo $CMD
VM_URL=$(eval $CMD)
VM_URL=(`echo $VM_URL|awk '{print $2;}'`)
echo
echo

echo "List all servers"
echo "Meaning: kamaki server list"
CMD="${BASE_CMD} $OCCI_ENDPOINT/compute"
echo $CMD
eval $CMD
echo
echo

echo "Details on server"
echo "Meaning: kamaki server info ${VM_URL}"
CMD="${BASE_CMD} ${VM_URL} > ${VM_INFO}"
echo $CMD
eval $CMD
echo
echo

STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
WAIT=10
while [ $STATE != 'active' ]
do
    echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
    sleep $WAIT
    let "WAIT++"
    eval $CMD
    STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
done
cat $VM_INFO
echo
echo

echo "STOP the server"
echo "Meaning: kamaki server shutdown"
ACTION="stop"
ACT="${BASE_CMD} -X POST ${VM_URL}?action=${ACTION} -H 'Category: ${ACTION} ;\
    scheme=\"http://schemas.ogf.org/occi/infrastructure/compute/action#\"; class=\"action\"'"
echo "$ACT"
eval $ACT
echo "Check server state"
echo $CMD
eval $CMD
STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
WAIT=5
while [ $STATE != 'inactive' ]
do
    echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
    sleep $WAIT
    let "WAIT++"
    eval $CMD
    STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
done
echo
echo

echo "START the server"
echo "Meaning: kamaki server start"
ACTION="start"
ACT="${BASE_CMD} -X POST ${VM_URL}?action=${ACTION} -H 'Category: ${ACTION} ;\
    scheme=\"http://schemas.ogf.org/occi/infrastructure/compute/action#\"; class=\"action\"'"
echo "$ACT"
eval $ACT
echo "Check server state"
echo $CMD
eval $CMD
STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
WAIT=5
while [ $STATE != 'active' ]
do
    echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
    sleep $WAIT
    let "WAIT++"
    eval $CMD
    STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
done
echo
echo


echo "RESTART the server"
echo "Meaning: kamaki server restart"
ACTION="restart"
ACT="${BASE_CMD} -X POST ${VM_URL}?action=${ACTION} -H 'Category: ${ACTION} ;\
    scheme=\"http://schemas.ogf.org/occi/infrastructure/compute/action#\"; class=\"action\"'"
echo "$ACT"
eval $ACT
echo "Check server state"
echo $CMD
eval $CMD
STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
WAIT=5
while [ $STATE != 'inactive' ]
do
    echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
    sleep $WAIT
    let "WAIT++"
    eval $CMD
    STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
done
echo
WAIT=5
while [ $STATE != 'active' ]
do
    echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
    sleep $WAIT
    let "WAIT++"
    eval $CMD
    STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
done
echo
echo


echo "Delete the server"
echo "Meaning: kamaki server delete ${VM_URL}"
CMD="${BASE_CMD} -X DELETE ${VM_URL}"
echo $CMD
eval $CMD
echo
echo

echo "Wait server to be destroyed"
CMD="${BASE_CMD} ${VM_URL} > ${VM_INFO}"
echo $CMD
eval $CMD

STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
WAIT=10
while [ $STATE == 'active' ]
do
    echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
    sleep $WAIT
    let "WAIT++"
    eval $CMD
    STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
done
echo


echo "Test create with context (PPK auth)"
echo "Meaning: kamaki server create --name \"My Test VM\" \\"
echo "    --flavor-id ${RESOURCE_TPL} --image-id ${OS_TPL}"
echo "    -p `pwd`/id_rsa.pub,/root/.ssh/authorized_keys,root,root,0600"

echo "Create a PPK pair:"
PPK_DIR="/tmp"
TIMESTAMP=`date +"%Y%m%d%H%M%s"`
PPK="ppk${TIMESTAMP}"
PPK_GEN_CMD="ssh-keygen -f ${PPK_DIR}/${PPK} -t rsa -N ''"
echo $PPK_GEN_CMD
eval $PPK_GEN_CMD
PUBLIC_KEY=`cat ${PPK_DIR}/${PPK}.pub`
echo "Public Key:"
echo $PUBLIC_KEY
echo
echo


CMD="${BASE_CMD} -X'POST' $OCCI_ENDPOINT/compute \
    -H'Category: compute; scheme=\"http://schemas.ogf.org/occi/infrastructure#\"; class=\"kind\"' \
    -H'Content-Type: text/occi' \
    -H'Category: ${RESOURCE_TPL}; scheme=\"http://schemas.openstack.org/template/resource#\"; class=\"mixin\"' \
    -H'Category: ${OS_TPL}; scheme=\"http://schemas.openstack.org/template/os#\"; class=\"mixin\"' \
    -H'X-OCCI-Attribute: occi.core.title=\"OCCI test VM\"' \
    -H 'Category: public_key; scheme=\"http://schemas.openstack.org/instance/credentials#\";class=\"mixin\"' \
    -H'X-OCCI-Attribute: org.openstack.credentials.publickey.name=\"${PPK}\"' \
    -H'X-OCCI-Attribute: org.openstack.credentials.publickey.data=\"${PUBLIC_KEY}\"'"
echo $CMD
VM_URL=$(eval $CMD)
echo $VM_URL
VM_URL=(`echo $VM_URL|awk '{print $2;}'`)
echo
echo


echo "Wait for server to get up"
CMD="${BASE_CMD} ${VM_URL} > ${VM_INFO}"
echo $CMD
eval $CMD

STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
WAIT=10
while [ $STATE != 'active' ]
do
    echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
    sleep $WAIT
    let "WAIT++"
    eval $CMD
    STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
done
echo

printf "Wait 16 seconds for the network |"
for i in `seq 1 4`; do
    sleep 1
    printf "\b/"
    sleep 1
    printf "\b-"
    sleep 1
    printf "\b\\"
    sleep 1
    printf "\b|"
done
echo "\b\b. Fingers crossed..."
echo

echo "Check PPK authentication"
VM_ID=(`echo ${VM_URL}|awk '/\//{n=split($0,a,"/"); print a[n]; }'`)
CMD="scp -o \"StrictHostKeyChecking no\" -i ${PPK_DIR}/${PPK} \
    root@snf-${VM_ID}.vm.okeanos.grnet.gr:/root/.ssh/authorized_keys \
    ${PPK_DIR}/${PPK}.downloaded"
echo $CMD
eval $CMD
if [ -f ${PPK_DIR}/${PPK}.downloaded ]; then
    echo "PPK authentication is OK"
else
    echo "PPK authentication FAILED"
fi
echo
echo

echo "Clean up"
CMD="${BASE_CMD} -X DELETE ${VM_URL}"
echo $CMD
eval $CMD
CMD="rm -f ${PPK_DIR}/${PPK}* ${VM_INFO}"
echo $CMD
eval $CMD
echo
echo
