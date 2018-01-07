#!/usr/bin/python

import os
import sys
import lfs

lfsbuilder_directory = os.path.dirname(os.path.realpath(sys.argv[0]))

# Enter the 'lfsbuilder.py' folder
os.chdir(lfsbuilder_directory)

# Create the LFS instance for the required builder
l = lfs.LFS("toolchain")
# l = lfs.LFS("system")
# l = lfs.LFS("configuration")

l.build()

# Delete created object
del l
