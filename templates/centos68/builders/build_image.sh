#!/usr/bin/env bash

PACKER_EXEC=/opt/packer
if [[ ! -x $PACKER_EXEC ]]; then
    echo "Packer not found!"
    exit 1
fi
echo $PACKER_EXEC

ISOURL="http://10.110.19.1/isos/CentOS-6.8-x86_64-minimal.iso"
OUTDIR=/tmp/centos68-$BUILD_TAG
IMGNAME=centos68x86_64-$BUILD_TAG.qcow2

echo "Build: "$BUILD_TAG
echo "GIT_COMMIT: "$GIT_COMMIT

echo "Workspace: "$WORKSPACE
cd $WORKSPACE
$PACKER_EXEC build -var "outdir=$OUTDIR" -var "vmname=$IMGNAME" -var "isourl=$ISOURL" centos68x86_64.json

generate_post_data()
{
    cat <<EOF
{
    "image_name":"$IMGNAME",
    "os_type":"Linux",
    "os_distro":"centos",
    "os_ver":"6.8",
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
    #mv $OUTDIR/$IMGNAME /var/www/html/images/build/
    virt-sysprep -a  $OUTDIR/$IMGNAME
    echo "scp the image to aibuild-image-server........"
	scp $OUTDIR/$IMGNAME root@aibuild-image-server.com:/var/www/html/build/

else
    echo "Image not generated successfully"
    exit 1
fi

# Clean
rm -rf $OUTDIR
