#!/bin/bash

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

BASE_CMD="curl -v -H 'X-Auth-Token: ${TOKEN}'"

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
    -H'X-OCCI-Attribute: occi.core.title=\"My test VM\"'"
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
CMD="${BASE_CMD} ${VM_URL} > vm.info"
echo $CMD
eval $CMD
echo
echo

STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' vm.info`)
WAIT=1;
while [ $STATE != 'active' ]
do
    echo "Server state is ${STATE}"
    echo "wait ${WAIT}\" and check again"
    sleep $WAIT;
    let "WAIT++";
    echo "$CMD";
    eval $CMD;
    STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' vm.info`)
done;
cat vm.info;
echo
echo


echo "Delete the server"
echo "Meaning: kamaki server delete ${VM_URL}"
CMD="${BASE_CMD} -X DELETE ${VM_URL}"
echo $CMD
eval $CMD
echo
echo
