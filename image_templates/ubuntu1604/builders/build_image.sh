#!/usr/bin/env bash

PACKER_EXEC=/opt/packer
if [[ ! -x $PACKER_EXEC ]]; then
    echo "Packer not found!"
    exit 1
fi
echo $PACKER_EXEC

OSNAME="ubuntu1604"
ISOURL=$ISOS_URL
WEBSERVER=$WEB_SERVER
OUTDIR=/tmp/$OSNAME"_"$BUILD_NUMBER
IMGNAME=$OSNAME"x86_64_"`date +%Y%m%d`"_"$BUILD_NUMBER.qcow2

echo "Build: "$BUILD_NUMBER
echo "GIT_COMMIT: "$GIT_COMMIT

echo "Workspace: "$WORKSPACE
cd $WORKSPACE
$PACKER_EXEC build -var "outdir=$OUTDIR" -var "vmname=$IMGNAME" -var "isourl=$ISOURL" ubuntu1604x86_64.json

generate_post_data()
{
    cat <<EOF
{
    "image_name":"$IMGNAME",
    "os_name":"$OSNAME",
    "update_contents":"$GIT_COMMIT",
    "get_url": "http://$WEB_SERVER/images/$OSNAME/$IMGNAME"
}
EOF
}

if [[ -e "$OUTDIR/$IMGNAME" ]]; then
    # Need add dns mapping for aibuild-server.com and hostip
    curl --header "Content-Type: application/json" \
      --request POST \
      --data "$(generate_post_data)" \
      http://aibuild-server.com:9753/v1/build

    virt-sysprep -a $OUTDIR/$IMGNAME
    # Move image to build dir
    WEBPATH="/var/www/html/images/$OSNAME"
    mkdir -p $WEBPATH
    mv $OUTDIR/$IMGNAME $WEBPATH
else
    echo "Image not generated successfully"
    exit 1
fi

# Clean
rm -rf $OUTDIR
