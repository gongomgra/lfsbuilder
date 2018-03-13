
import os
import sys

import config
import tools

def set_attributes(component_data_dict, parent_function):

    # Call parent_function
    parent_function()

    # Command to generate img
    post_text = """echo "Mounting '@@LFS_IMG_FILENAME@@' image. This may take a while..."

# Get available loop device
available_loop_device=$(losetup -f)

# Mount image file to this loop device
losetup ${available_loop_device} @@LFS_IMG_FILENAME@@

# Mount loop device to BASE_DIRECTORY
mount -v ${available_loop_device} $LFS
"""
    post_text = post_text.replace("@@LFS_IMG_FILENAME@@", config.IMG_FILENAME)

    tools.add_to_dictionary(component_data_dict, "post", post_text, concat=False)

    # Run component from the 'lfsbuilder_tmp_directory'
    tools.add_to_dictionary(component_data_dict,
                            key="build_directory_path",
                            value=component_data_dict["lfsbuilder_tmp_directory"],
                            concat=False)

    tools.add_to_dictionary(component_data_dict,
                            key="extracted_directory",
                            value=component_data_dict["lfsbuilder_tmp_directory"],
                            concat=False)

    # We will move back to that directory after building the component
    tools.add_to_dictionary(component_data_dict,
                            key="sources_directory",
                            value=component_data_dict["lfsbuilder_src_directory"],
                            concat=False)
