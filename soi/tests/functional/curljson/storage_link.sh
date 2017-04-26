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

echo "Creating temp directory"
TEMP_DIR=`mktemp -d`

function cleanup { 
	rm -rf "$TEMP_DIR"
	echo "Deleted temp working directory $TEMP_DIR"
}
trap cleanup EXIT

if [ -z "$SNF_OCCI_DEBUG" ]; then
	XARGS="-s";
else 
	XARGS="-v";
fi

BASE_CMD="curl ${XARGS} -H'X-Auth-Token: ${TOKEN}'"
VM_INFO="/tmp/vm.info"

echo "Preparation ..."
echo "... create a VM"

echo "Create a server"
echo "Meaning: kamaki server create --name \"My Test VM\" \\"
echo "	--flavor-id ${RESOURCE_TPL} --image-id ${OS_TPL}"

cat > $TEMP_DIR/json << EOF
{
	"kind": "http://schemas.ogf.org/occi/infrastructure#compute",
	"mixins": [
		"http://schemas.openstack.org/template/os#$OS_TPL",
		"http://schemas.openstack.org/template/resource#$RESOURCE_TPL"
	],
	"attributes": {
		"occi.core.title": "OCCI test VM"
	}
}
EOF

CMD="${BASE_CMD} -X'POST' $OCCI_ENDPOINT/compute \
	-H'Content-Type: application/occi+json' \
	-d @$TEMP_DIR/json"
echo $CMD
VM=$(eval $CMD)
echo $VM
VM_URL=(`echo $VM|awk '{print $2;}'`)
VM_ID=(`echo $VM_URL|awk '{n=split($0,a,"/"); print a[n];}'`)

echo "... create a volume"

cat > $TEMP_DIR/json << EOF
{
	"kind": "http://schemas.ogf.org/occi/infrastructure#storage",
	"attributes": {
		"occi.core.title": "My Test Volume",
		"occi.storage.size": 10
	}
}
EOF

CMD="${BASE_CMD} -X'POST' $OCCI_ENDPOINT/storage/ \
	-H'Content-Type: application/occi+json' \
	-d @$TEMP_DIR/json"
echo $CMD
VOLUME=$(eval $CMD)
VOLUME_URL=(`echo ${VOLUME}|awk '{print $2;}'`)
echo ${VOLUME_URL}
VOLUME_ID=(`echo ${VOLUME_URL}|awk '{n=split($0,a,"/"); print a[n];}'`)

echo "... wait while server boots"
CMD="${BASE_CMD} ${VM_URL} > ${VM_INFO}"
echo $CMD
eval $CMD
STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
WAIT=10
while [ $STATE != 'active' ]
do
	echo "... server state is ${STATE}, wait ${WAIT}\" and check again"
	sleep $WAIT
	let "WAIT++"
	eval $CMD
	STATE=(`awk '/occi.compute.state/{n=split($0,a,"\""); print a[2];}' ${VM_INFO}`)
done
echo "... server state is ${STATE}"
echo
echo


echo "Attach volume to server"
echo "Meaning: kamaki server attach ${VM_ID} --volume-id ${VOLUME_ID}"
cat > $TEMP_DIR/json << EOF
{
	"kind": "http://schemas.ogf.org/occi/infrastructure#storagelink",
	"attributes": {
		"occi.core.target": "$VOLUME_URL",
		"occi.core.source": "$VM_URL"
	}
}
EOF

CMD="${BASE_CMD} -X'POST' $OCCI_ENDPOINT/storagelink/ \
	-H'Content-Type: application/occi+json' \
	-d @$TEMP_DIR/json"
echo $CMD
LINK=$(eval $CMD)
echo $LINK
LINK_URL=(`echo ${LINK}|awk '{print $2}'`)
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

echo "List volume attachments"
echo "Meaning: kamaki server attachments ${VM_ID}"
CMD="${BASE_CMD} ${OCCI_ENDPOINT}/storagelink/"
echo $CMD
eval $CMD
echo
echo

echo "Information on this particular storage link"
echo "Meaning: kamaki server attachment ${VM_ID} --attachment-id ${VOLUME_ID}"
CMD="${BASE_CMD} ${LINK_URL}"
echo $CMD
eval $CMD
echo
echo

echo "Detach volume from server"
echo "Meaning: kamaki server detach ${VM_ID} --volume-id ${VOLUME_ID}"
CMD="${BASE_CMD} -XDELETE ${LINK_URL}"
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
CMD="${BASE_CMD} -X'DELETE' $OCCI_ENDPOINT/storage/${VOLUME_ID}"
echo "$CMD"
eval $CMD
echo
CMD="${BASE_CMD} -X DELETE ${VM_URL}"
echo $CMD
eval $CMD
CMD="rm -f ${VM_INFO}"
echo $CMD
eval $CMD
echo
