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
fi

echo "Vars OK, run tests"
echo
echo

BASE_CMD="occi ${XARGS} --endpoint ${OCCI_ENDPOINT} ${AUTH}"
VM_INFO="/tmp/vm.info"

echo "Create a (private) network"
echo "Equivalent: kamaki network create --name \"My Test Network\" \\"

CMD="${BASE_CMD} --action create --resource network "
CMD="${CMD} --mixin 'http://schemas.ogf.org/occi/infrastructure/network#ipnetwork'"
CMD="${CMD} --attribute occi.core.title=\"My Test Network\""
CMD="${CMD} --attribute occi.network.address=\"192.168.0.0/24\""
echo $CMD
NETWORK_URL=$(eval $CMD)
echo $NETWORK_URL
NETWORK_ID=(`echo $NETWORK_URL|awk -F/ '{print $NF;}'`)
echo ${NETWORK_ID}
echo
echo

echo "Retrieve network information"
echo "Equivalent: kamaki network info ${NETWORK_ID}"
CMD="${BASE_CMD} --action describe --resource ${NETWORK_URL} "
echo $CMD
eval $CMD
echo
echo


echo "Retrieve network information"
echo "Equivalent: kamaki network list"
CMD="${BASE_CMD} --action list --resource network "
echo $CMD
NET_LIST=$(eval $CMD)
echo $NET_LIST
echo
echo

PUB_NET_URL=(`echo $NET_LIST|awk -F=" " '{print $1;}'`)
echo $PUB_NET_URL

PUB_NET_ID=(`echo $PUB_NET_URL|awk -F/ '{print $NF;}'`)
echo $PUB_NET_ID

echo "... create a server instance"
CMD="${BASE_CMD} --action create --resource compute "
CMD="${CMD} --attribute occi.core.title=\"OCCI test VM\""
CMD="${CMD} --mixin os_tpl#${OS_TPL} --mixin resource_tpl#${RESOURCE_TPL}"
echo "$CMD"
VM_URL=$(eval $CMD)
echo $VM_URL
VM_SUFFIX=(`echo ${VM_URL}|awk '{n=split($0,a,"/"); print "/"a[n-1]"/"a[n]}'`)

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


echo "Attach private network to server"
CMD="${BASE_CMD} --action link --resource ${VM_URL} "
CMD="${CMD} --link ${NETWORK_URL}"
echo $CMD
NETWORK_LINK_PRIVATE_URL=$(eval $CMD)
echo $NETWORK_LINK_PRIVATE_URL
NETWORK_LINK_PRIVATE_ID=(`echo $NETWORK_LINK_PRIVATE_URL|awk -F/ '{print $NF;}'`)
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


echo "Attach public network to server"
CMD="${BASE_CMD} --action link --resource ${VM_URL} "
CMD="${CMD} --link ${PUB_NET_URL}"
echo $CMD
NETWORK_LINK_PUBLIC_URL=$(eval $CMD)
echo $NETWORK_LINK_PUBLIC_URL
NETWORK_LINK_PUBLIC_ID=(`echo $NETWORK_LINK_PUBLIC_URL|awk -F/ '{print $NF;}'`)
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

echo "Get information on network link"
CMD="${BASE_CMD} --action describe --resource ${NETWORK_LINK_PRIVATE_URL} "
echo $CMD
eval $CMD
echo
echo

echo "Get information on public link"
CMD="${BASE_CMD} --action describe --resource ${NETWORK_LINK_PUBLIC_URL} "
echo $CMD
eval $CMD
echo
echo

echo "List network links"
echo "Not supported by rocci(?)."
echo
echo


echo "Detach private network from server (delete networklink)"
echo "Not supported by rocci(buggy functionality-deletes the specified VM)"
echo
echo


echo "Detach public network from server (delete networklink)"
echo "Not supported by rocci(buggy functionality-deletes the specified VM)"
echo
echo

echo "... clean up"
CMD="${BASE_CMD} --action delete --resource ${VM_SUFFIX}";
echo $CMD
eval $CMD

printf "The server is being deleted...  "
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
CMD="${BASE_CMD} --action delete --resource /network/${NETWORK_ID}"
echo $CMD
eval $CMD
CMD="rm -f ${VM_INFO}"
echo $CMD
eval $CMD
echo





