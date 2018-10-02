#!/usr/bin/env bash

PACKER_EXEC=/opt/packer
if [[ ! -x $PACKER_EXEC ]]; then
    echo "Packer not found!"
    exit 1
fi
echo $PACKER_EXEC

ISOURL=http://releases.ubuntu.com/16.04.5/ubuntu-16.04.5-server-amd64.iso
OUTDIR=/tmp/ubuntu1604-$BUILD_TAG
IMGNAME=ubuntu1604x86_64-$BUILD_TAG.qcow2
CHANGE=$CHANGE_TITLE

echo "Change: "$CHANGE
echo "Build: "$BUILD_TAG

echo "Workspace: "$WORKSPACE
cd $WORKSPACE
$PACKER_EXEC build -var "outdir=$OUTDIR" -var "vmname=$IMGNAME" -var "isourl=$ISOURL" ubuntu1604.json

curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"image_name":"$IMGNAME","os_type":"Linux","os_distro":"ubuntu","os_ver":"16.04","from_iso":"$ISOURL","update_contents":"$CHANGE"}' \
  http://172.23.61.4:9753/v1/build
