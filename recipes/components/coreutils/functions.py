
import os
import sys

import config
import tools

def apply_patches(component_data_dict, parent_function):

    if component_data_dict["builder_name"] == "toolchain":
        # coreutils should not apply patches while building the toolchain
        # reference: http://lfs-support.linuxfromscratch.narkive.com/CLsG3Tyw/5-18-1-coreutils-8-23
        pass
    else:
        parent_function()
