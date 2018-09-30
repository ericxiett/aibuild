#!/usr/bin/env bash

OUTDIR="/tmp/packer-output-ubuntu1604"
if [[ -d $OUTDIR ]]; then
    rm -rf $OUTDIR
fi
mkdir $OUTDIR

PACKER_EXEC=/root/packer
if [[ ! -x $PACKER_EXEC ]]; then
    echo "Packer not found!"
    exit 1
fi
$PACKER_EXEC
