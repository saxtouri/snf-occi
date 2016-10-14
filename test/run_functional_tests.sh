#!/bin/bash

echo "Check vars ..."

if [ -z "$OCCI_ENDPOINT" ]; then echo "E: OCCI_ENDPOINT not set"; exit 1; fi;
echo "OCCI_ENDPOINT = ${OCCI_ENDPOINT}"

if [ -z "$USER_PROXY" ]; then echo "E: USER_PROXY not set"; exit 1; fi;
echo "USER_PROXY = ${USER_PROXY}"

if [ -z "$OS_TPL" ]; then echo "E: OS_TPL not set"; exit 1; fi;
echo "OS_TPL = ${OS_TPL}"

if [ -z "$RESOURCE_TPL" ]; then echo "E: RESOURCE_TPL not set"; exit 1; fi;
echo "RESOURCE_TPL = ${RESOURCE_TPL}";

echo "Vars OK, run tests"
echo


BASE_CMD="occi --endpoint ${OCCI_ENDPOINT} -n x509 -X --user-cred ${USER_PROXY}"


echo "List OS templates"
echo "Meaning: kamaki image list"
CMD="${BASE_CMD} --action list --resource os_tpl"
echo "$CMD"
eval $CMD
echo

echo "List resource templates"
echo "Meaning: kamaki flavor list"
CMD="${BASE_CMD} --action list --resource resource_tpl"
echo "$CMD"
eval $CMD
echo

echo "Details on OS template"
echo "Meaning: kamaki image info <ID of ${OS_TPL} image>"
CMD="${BASE_CMD} --action describe --resource os_tpl#${OS_TPL}"
echo "$CMD"
eval $CMD
echo

echo "Details on resource template"
echo "Meaning: kamaki flavor info <FLAVOR ID of ${RESOURCE_TPL}>"
CMD="${BASE_CMD} --action describe --resource resource_tpl#${RESOURCE_TPL}"
echo "$CMD"
eval $CMD
echo

echo "Create a server instance"
echo "Meaning: kamaki server create --name \"My Test VM\" \\"
echo "    --flavor-id <ID of c2r2048d40drb> --image-id <ID of ${OS_TPL}>"
CMD="${BASE_CMD} --action create --resource compute "
CMD="${CMD} --attribute occi.core.title=\"My Test VM\""
CMD="${CMD} --mixin os_tpl#${OS_TPL} --mixin resource_tpl#${RESOURCE_TPL}"
echo "$CMD"
VM_URL=$(eval $CMD)
echo "VM URL: ${VM_URL}"
echo

echo "List server instances"
echo "Meaning: kamaki server list"
CMD="${BASE_CMD} --action list --resource compute"
echo "$CMD"
eval $CMD
echo

if [ -z "$VM_URL" ]; then
    echo "Frankly, I don't know what servers to describe or delete";
else
    SUFFIX=(`echo ${VM_URL}|awk '{n=split($0,a,"/"); print "/"a[n-1]"/"a[n]}'`)

    echo "Details on server instance ${SUFFIX}";
    echo "Meaning: kamaki server info ${SERVER_URL}";
    CMD="${BASE_CMD} --action describe --resource ${SUFFIX} > vm.info";
    echo "$CMD";
    eval $CMD;
    STATE=(`awk '/occi.compute.state/{n=split($0,a," = "); print a[2];}' vm.info`)

    WAIT=1;
    while [ $STATE != 'active' ]
    do
        echo "Server state is ${STATE}"
        echo "wait ${WAIT}\" and check again"
        sleep $WAIT;
        let "WAIT++";
        echo "$CMD";
        eval $CMD;
        STATE=(`awk '/occi.compute.state/{n=split($0,a," = "); print a[2];}' vm.info`);
    done;
    cat vm.info;

    echo "Destroy server instance ${SUFFIX}";
    echo "Meaning: kamaki server delete ${SERVER_URL}";
    CMD="${BASE_CMD} --action delete --resource ${SUFFIX}";
    echo "$CMD";
    eval $CMD;
fi;
echo
