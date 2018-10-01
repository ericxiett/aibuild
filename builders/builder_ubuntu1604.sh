#!/usr/bin/env bash

PACKER_EXEC=/opt/packer
if [[ ! -x $PACKER_EXEC ]]; then
    echo "Packer not found!"
    exit 1
fi
echo $PACKER_EXEC

OUTDIR=/tmp/ubuntu1604-$BUILD_TAG
IMGNAME=ubuntu1604x86_64-$BUILD_TAG.qcow2
CHANGE=$CHANGE_TITLE

echo "Change: "$CHANGE
echo "Build: "$BUILD_TAG

echo "Workspace: "$WORKSPACE
cd $WORKSPACE
$PACKER_EXEC build -var "outdir=$OUTDIR" -var "vmname=$IMGNAME" ubuntu1604.json
