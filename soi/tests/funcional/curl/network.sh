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

if [ -z "$OS_TPL" ]; then echo "E: OS_TPL not set"; exit 1; fi;
echo "OS_TPL = ${OS_TPL}"

if [ -z "$RESOURCE_TPL" ]; then echo "E: RESOURCE_TPL not set"; exit 1; fi;
echo "RESOURCE_TPL = ${RESOURCE_TPL}";

if [ -z "$FREE_IP" ]; then echo "E: FREE_IP not set"; exit 1; fi;
echo "FREE_IP = ${FREE_IP}";

echo "Vars OK, run tests"
echo

if [ -z "$SNF_OCCI_DEBUG" ]; then
    XARGS="-s";
else 
    XARGS="-v";
fi

BASE_CMD="curl ${XARGS} -H'X-Auth-Token: ${TOKEN}'"
VM_INFO="/tmp/vm.info"


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
NETWORK_URL=(`echo $NETWORK_URL|awk '{print $2;}'`)
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
NET_LIST=$(eval $CMD)
echo $NET_LIST
echo
echo

# Get the first network in the list, assume it is a public network
PUB_NET_URL=(`echo $NET_LIST|awk '{
    split($0, net_list, " ");
    print(net_list[2]);
}'`)
PUB_NET_ID=(`echo $PUB_NET_URL|awk '{
    n=split($0,net_url, "/");
    print net_url[n];
}'`)

echo "Create a server"
CMD="${BASE_CMD} -X'POST' $OCCI_ENDPOINT/compute \
    -H'Category: compute; scheme=\"http://schemas.ogf.org/occi/infrastructure#\"; class=\"kind\"' \
    -H'Content-Type: text/occi' \
    -H'Category: ${RESOURCE_TPL}; scheme=\"http://schemas.openstack.org/template/resource#\"; class=\"mixin\"' \
    -H'Category: ${OS_TPL}; scheme=\"http://schemas.openstack.org/template/os#\"; class=\"mixin\"' \
    -H'X-OCCI-Attribute: occi.core.title=\"OCCI test VM\"'"
echo $CMD
VM_URL=$(eval $CMD)
VM_URL=(`echo $VM_URL|awk '{print $2;}'`)
VM_ID=(`echo ${VM_URL}|awk '/\//{n=split($0,a,"/"); print a[n]; }'`)
echo "Wait until server is ready"
CMD="${BASE_CMD} ${VM_URL} > ${VM_INFO}"
echo $CMD
eval $CMD
STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
echo $STATE
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

echo "Attach private network to server"
CMD="${BASE_CMD} -X'POST' $OCCI_ENDPOINT/networklink/ \
    -H 'Category: networkinterface; \
        scheme=\"http://schemas.ogf.org/occi/infrastructure#\"; \
        class=\"kind\";' \
    -H 'X-OCCI-Attribute: occi.core.target=${NETWORK_URL},\
        occi.core.source=${VM_URL}'"
echo $CMD
LINK_URL=$(eval $CMD)
LINK_URL=(`echo $LINK_URL|awk '{print $2;}'`)
echo ${LINK_URL}
LINK_ID=(`echo $NETWORK_URL|awk '{n=split($0,a,"/"); print a[n];}'`)
echo
echo
printf "The network is being attached  "
for i in `seq 1 20`; do
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

echo "Attach public network"
CMD="${BASE_CMD} -X'POST' $OCCI_ENDPOINT/networklink/ \
    -H 'Category: networkinterface; \
        scheme=\"http://schemas.ogf.org/occi/infrastructure#\"; \
        class=\"kind\";' \
    -H 'X-OCCI-Attribute: occi.core.target=${PUB_NET_URL},\
        occi.core.source=${VM_URL}'"
echo $CMD
PUB_LINK_URL=$(eval $CMD)
PUB_LINK_URL=(`echo $PUB_LINK_URL|awk '{print $2;}'`)
echo ${PUB_LINK_URL}
PUB_LINK_ID=(`echo $PUB_NET_URL|awk '{n=split($0,a,"/"); print a[n];}'`)
echo
printf "The network is being attached  "
for i in `seq 1 20`; do
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

echo "Get information on network link"
CMD="${BASE_CMD} ${LINK_URL}"
echo $CMD
eval $CMD
echo
echo

echo "Get information on public link"
CMD="${BASE_CMD} ${PUB_LINK_URL}"
echo $CMD
eval $CMD
echo
echo


echo "List network links"
CMD="${BASE_CMD} ${OCCI_ENDPOINT}/networklink"
echo $CMD
eval $CMD
echo
echo

echo "Remove private network from server"
CMD="${BASE_CMD} -X'DELETE' ${LINK_URL}"
echo $CMD
eval $CMD
printf "The network is being detached  "
for i in `seq 1 20`; do
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

echo "Remove public network from server"
CMD="${BASE_CMD} -X'DELETE' ${PUB_LINK_URL}"
echo $CMD
eval $CMD
printf "The network is being detached  "
for i in `seq 1 20`; do
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

echo "Delete network"
echo "Equivalent: kamaki network delete ${NETWORK_ID}"
CMD="${BASE_CMD} -X'DELETE' ${NETWORK_URL}"
echo $CMD
eval $CMD
echo
echo

echo "Clean Up"
CMD="${BASE_CMD} -X DELETE ${VM_URL}"
echo $CMD
eval $CMD
CMD="rm -f ${VM_INFO}"
echo $CMD
eval $CMD
echo
