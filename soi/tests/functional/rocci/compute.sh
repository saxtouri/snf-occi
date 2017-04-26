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
fi

echo "Vars OK, run tests"
echo
echo


BASE_CMD="occi ${XARGS} --endpoint ${OCCI_ENDPOINT} ${AUTH}"
VM_INFO="/tmp/vm.info"

echo "List OS templates"
echo "Meaning: kamaki image list"
CMD="${BASE_CMD} --action list --resource os_tpl"
echo "$CMD"
eval $CMD
echo
echo

echo "List resource templates"
echo "Meaning: kamaki flavor list"
CMD="${BASE_CMD} --action list --resource resource_tpl"
echo "$CMD"
eval $CMD
echo
echo

echo "Details on OS template"
echo "Meaning: kamaki image info ${OS_TPL}"
CMD="${BASE_CMD} --action describe --resource os_tpl#${OS_TPL}"
echo "$CMD"
eval $CMD
echo
echo

echo "Details on resource template"
echo "Meaning: kamaki flavor info ${RESOURCE_TPL}"
CMD="${BASE_CMD} --action describe --resource resource_tpl#${RESOURCE_TPL}"
echo "$CMD"
eval $CMD
echo
echo

echo "Create a server instance"
echo "Meaning: kamaki server create --name \"OCCI test VM\" \\"
echo "    --flavor-id ${RESOURCE_TPL} --image-id ${OS_TPL}"
CMD="${BASE_CMD} --action create --resource compute "
CMD="${CMD} --attribute occi.core.title=\"OCCI test VM\""
CMD="${CMD} --mixin os_tpl#${OS_TPL} --mixin resource_tpl#${RESOURCE_TPL}"
echo "$CMD"
VM_URL=$(eval $CMD)
echo "VM URL: ${VM_URL}"
echo
echo

echo "List server instances"
echo "Meaning: kamaki server list"
CMD="${BASE_CMD} --action list --resource compute"
echo "$CMD"
eval $CMD
echo
echo

if [ -z "$VM_URL" ]; then
    echo "Frankly, I don't know what servers to describe or delete";
else
    SUFFIX=(`echo ${VM_URL}|awk '{n=split($0,a,"/"); print "/"a[n-1]"/"a[n]}'`)

    echo "Details on server instance ${SUFFIX}";
    echo "Meaning: kamaki server info ${SERVER_URL}";
    CMD="${BASE_CMD} --action describe --resource ${SUFFIX} > ${VM_INFO}";
    echo "$CMD";
    eval $CMD;
    STATE=(`awk '/occi.compute.state/{n=split($0,a," = "); print a[2];}' ${VM_INFO}`)

    WAIT=10;
    while [ $STATE != 'active' ]
    do
        echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
        sleep $WAIT;
        let "WAIT++";
        eval $CMD;
        STATE=(`awk '/occi.compute.state/{n=split($0,a," = "); print a[2];}' ${VM_INFO}`);
    done;
    cat $VM_INFO;

    echo "STOP server"
    echo "Meaning: kamaki server shutdown ${SERVER_URL}"
    ACTION="stop"
    ACMD="${BASE_CMD} --resource ${SUFFIX} --action trigger --trigger-action ${ACTION}"
    echo "$ACMD"
    eval $ACMD
    WAIT=5;
    while [ $STATE != 'inactive' ]
    do
        echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
        sleep $WAIT;
        let "WAIT++";
        eval $CMD;
        STATE=(`awk '/occi.compute.state/{n=split($0,a," = "); print a[2];}' ${VM_INFO}`);
    done;
    echo "Server state is $STATE"
    echo

    echo "START server"
    echo "Meaning: kamaki server start ${SERVER_URL}"
    ACTION="start"
    ACMD="${BASE_CMD} --resource ${SUFFIX} --action trigger --trigger-action ${ACTION}"
    echo "$ACMD"
    eval $ACMD
    WAIT=5;
    while [ $STATE != 'active' ]
    do
        echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
        sleep $WAIT;
        let "WAIT++";
        eval $CMD;
        STATE=(`awk '/occi.compute.state/{n=split($0,a," = "); print a[2];}' ${VM_INFO}`);
    done;
    echo "Server state is $STATE"
    echo

    echo "RESTART server"
    echo "Meaning: kamaki server restart ${SERVER_URL}"
    ACTION="restart"
    ACMD="${BASE_CMD} --resource ${SUFFIX} --action trigger --trigger-action ${ACTION}"
    echo "$ACMD"
    eval $ACMD
    echo

    sleep 10

    WAIT=5;
    while [ $STATE != 'active' ]
    do
        echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
        sleep $WAIT;
        let "WAIT++";
        eval $CMD;
        STATE=(`awk '/occi.compute.state/{n=split($0,a," = "); print a[2];}' ${VM_INFO}`);
    done;
    echo "Server state is $STATE"
    echo

    echo "Destroy server instance ${SUFFIX}";
    echo "Meaning: kamaki server delete ${SERVER_URL}";
    ACMD="${BASE_CMD} --action delete --resource ${SUFFIX}";
    echo "$ACMD";
    eval $ACMD;

    WAIT=5;
    while [ $STATE == 'active' ]
    do
        echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
        sleep $WAIT;
        let "WAIT++";
        eval $CMD;
        STATE=(`awk '/occi.compute.state/{n=split($0,a," = "); print a[2];}' ${VM_INFO}`);
    done;
    echo "Server state is $STATE"
    echo
fi;
echo
echo

echo "Check contextualization"
echo

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

echo "Create a server instance with PPK"
echo "Meaning: kamaki server create --name \"OCCI test VM\" \\"
echo "    --flavor-id ${RESOURCE_TPL} --image-id ${OS_TPL} \\"
echo "    -p `pwd`/id_rsa.pub,/root/.ssh/authorized_keys,root,root,0600"
CMD="${BASE_CMD} --action create --resource compute"
CMD="${CMD} --attribute occi.core.title=\"OCCI test VM\""
CMD="${CMD} --mixin os_tpl#${OS_TPL} --mixin resource_tpl#${RESOURCE_TPL}"
CMD="${CMD} --context public_key='${PUBLIC_KEY}'"
echo "$CMD"
VM_URL=$(eval $CMD)
echo "VM URL: ${VM_URL}"
SUFFIX=(`echo ${VM_URL}|awk '{n=split($0,a,"/"); print "/"a[n-1]"/"a[n]}'`)
echo
echo

echo "Wait for server to get up"
CMD="${BASE_CMD} --action describe --resource ${SUFFIX} > ${VM_INFO}";
echo "$CMD";
eval $CMD;
STATE=(`awk '/occi.compute.state/{n=split($0,a," = "); print a[2];}' ${VM_INFO}`)

WAIT=10;
while [ $STATE != 'active' ]
do
    echo "Server state is ${STATE}, wait ${WAIT}\" and check again"
    sleep $WAIT;
    let "WAIT++";
    eval $CMD;
    STATE=(`awk '/occi.compute.state/{n=split($0,a," = "); print a[2];}' ${VM_INFO}`);
done;
echo
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
VM_ID=(`echo ${SUFFIX}|awk '/\//{n=split($0,a,"/"); print a[n]; }'`)
CMD="scp -o \"StrictHostKeyChecking no\" -i ${PPK_DIR}/${PPK} root@snf-${VM_ID}.vm.okeanos.grnet.gr:/root/.ssh/authorized_keys ${PPK_DIR}/${PPK}.downloaded"
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
CMD="${BASE_CMD} --action delete --resource ${SUFFIX}";
echo $CMD
eval $CMD
CMD="rm -f ${PPK_DIR}/${PPK}* ${VM_INFO}"
echo $CMD
eval $CMD
echo
echo
