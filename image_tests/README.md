# Test cases for images

## Intro
After building images for GuestOS, the images MUST be tested.

Some testcases can be used for many GuestOS images.

## Usage
In the builders of Jenkins, use shell method to build
``` bash
#!/bin/bash

set -e
cd $WORKSPACE
python execute_testcases.py image extended_size distro version user pass
# python execute_testcases.py http://xxx/images/centos65/centos65x86_64
# -5.qcow2 60 centos 6.5 root Lc13yfwpW
```


## Develop
execute_testcases.py: The only entry for testing

common/: common functions

testcases/: all testcases

- generic_testcases.py: Generic test cases for linux and windows
