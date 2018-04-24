
import os
import sys

import config
import tools
import printer

def get_components_to_build_list(builder_data_dict, parent_function):

    # Call parent function
    parent_function()

    # Remove unnecessary components
    if config.GENERATE_IMG_FILE is False:
        try:
            builder_data_dict["components_to_build"].remove("imggenerator")
        except ValueError:
            pass

    if config.MOUNT_IMG_FILE is False:
        try:
            builder_data_dict["components_to_build"].remove("imgmount")
        except ValueError:
            pass

    if config.MOUNT_SYSTEM_BUILDER_DIRECTORIES is False:
        try:
            builder_data_dict["components_to_build"].remove("mount")
        except ValueError:
            pass

    if config.MOUNT_SOURCES_DIRECTORY is False:
        try:
            builder_data_dict["components_to_build"].remove("sources")
        except ValueError:
            pass
