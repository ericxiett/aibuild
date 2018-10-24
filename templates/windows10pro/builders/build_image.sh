#!/usr/bin/env bash

PACKER_EXEC=/opt/packer
if [[ ! -x $PACKER_EXEC ]]; then
    echo "Packer not found!"
    exit 1
fi
echo $PACKER_EXEC

ISOURL="http://10.2.32.9/isos/cn_windows_10_consumer_edition_version_1803_updated_sep_2018_x64_dvd_a3fcbed0.iso"
OUTDIR=/tmp/WIN10PROX86_64-$BUILD_TAG
IMGNAME=WIN10PROX86_64-$BUILD_TAG.qcow2
GIT_COMMIT=sjt-test

echo "Build: "$BUILD_TAG
echo "GIT_COMMIT: "$GIT_COMMIT

echo "Workspace: "$WORKSPACE
cd $WORKSPACE
$PACKER_EXEC build -debug -var "outdir=$OUTDIR" -var "vmname=$IMGNAME" -var "isourl=$ISOURL" WIN10PROx86_64.json

generate_post_data()
{
    cat <<EOF
{
    "image_name":"$IMGNAME",
    "os_type":"Windows",
    "os_distro":"Windows",
    "os_ver":"10 1803",
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
