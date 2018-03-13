
import os
import sys

import config
import tools

def set_attributes(component_data_dict, parent_function):

    # Call parent_function
    parent_function()

    # Create destination directories just in case
    tools.add_to_dictionary(component_data_dict,
                            key="post",
                            value="mkdir -pv $LFS/{dev,proc,sys,run}")

    # Try to add mount commands for every directory
    for directory in sorted(component_data_dict["mount_commands"].keys()):
        if os.path.ismount(os.path.join(config.BASE_DIRECTORY, directory)) is False:
            tools.add_to_dictionary(component_data_dict,
                                    key="post",
                                    value=component_data_dict["mount_commands"][directory])


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
