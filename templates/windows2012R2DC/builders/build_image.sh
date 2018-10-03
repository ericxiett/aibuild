#!/usr/bin/env bash

PACKER_EXEC=/opt/packer
if [[ ! -x $PACKER_EXEC ]]; then
    echo "Packer not found!"
    exit 1
fi
echo $PACKER_EXEC

ISOURL="http://172.23.11.11/iso/windows/2012R2/SW_DVD9_Windows_Svr_Std_and_DataCtr_2012_R2_64Bit_ChnSimp_-4_MLF_X19-82889.ISO"
OUTDIR=/tmp/WIN2012R2DC-$BUILD_TAG
IMGNAME=WIN2012R2DCx86_64-$BUILD_TAG.qcow2

echo "Build: "$BUILD_TAG
echo "GIT_COMMIT: "$GIT_COMMIT

echo "Workspace: "$WORKSPACE
cd $WORKSPACE
$PACKER_EXEC build -var "outdir=$OUTDIR" -var "vmname=$IMGNAME" -var "isourl=$ISOURL" WIN2012R2DCx86_64.json

generate_post_data()
{
    cat <<EOF
{
    "image_name":"$IMGNAME",
    "os_type":"Windows",
    "os_distro":"Windows",
    "os_ver":"2012 R2 DC",
    "from_iso":"$ISOURL",
    "update_contents":"$GIT_COMMIT"
}
EOF
}

if [[ -e "$OUTDIR/$IMGNAME" ]]; then
    # Need add dns mapping for aibuild-server.com and hostip
    curl --header "Content-Type: application/json" \
      --request POST \
      --data "$(generate_post_data)" \
      http://aibuild-server.com:9753/v1/build

    # Move image to build dir
    mv $OUTDIR/$IMGNAME /var/www/html/images/build/
else
    echo "Image not generated successfully"
    exit 1
fi

# Clean
rm -rf $OUTDIR
