#!/usr/bin/python

import lfs

l = lfs.LFS("toolchain")
# l = lfs.LFS("system")
# l = lfs.LFS("configuration")

l.build()

# Delete created object
del l
