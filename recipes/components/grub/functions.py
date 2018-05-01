
import os
import sys

import config
import tools

def set_attributes(component_data_dict, parent_function):

    # Call parent_function
    parent_function()

    if component_data_dict["builder_name"] == "configuration":
        # Build this component from outside the chroot
        tools.add_to_dictionary(component_data_dict, key="build_into_chroot", value=False, concat=False)
        tools.add_to_dictionary(component_data_dict, key="run_as_username", value="root", concat=False)
