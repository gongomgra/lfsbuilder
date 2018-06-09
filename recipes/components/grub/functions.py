
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

        # Set 'config.GRUB_ROOT_PARTITION_NAME' with stored value in the 'tmp/loop_device.txt'
        # file if present.
        loop_device = os.path.join(
            component_data_dict["lfsbuilder_tmp_directory"],
            "loop_device.txt"
        )

        if os.path.exists(loop_device) is True:
            component_data_dict["component_substitution_list"].extend(
                [
                    config.GRUB_ROOT_PARTITION_NAME,
                    tools.read_file(loop_device)
                ]
            )
