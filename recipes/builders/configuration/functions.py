
import os
import sys

import config
import tools
import printer

def set_attributes(builder_data_dict, parent_function):

    # We remove the 'reboot' component because it will fail
    # when umounting the 'BASE_DIRECTORY' because it is in use (the 'setenv.sh' file).
    # The left the 'umount' component to do the work later within the 'collector' builder.
    try:
        builder_data_dict["components_to_build"].remove("reboot")
    except ValueError:
        pass

    # Call parent function
    parent_function()
