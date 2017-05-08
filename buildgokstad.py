#!/usr/bin/python

import lfs

l = lfs.LFS("toolchain")
# l = lfs.LFS("system")

l.build()

# Delete created object
del l
