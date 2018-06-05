
import os
import sys

import config
import tools

def set_attributes(component_data_dict, parent_function):

    # Call parent_function
    parent_function()

    tools.add_to_dictionary(component_data_dict, key="post", value="")

    # Generate 'umount' commands from 'component_data_dict["umount_directories"]'
    for d in component_data_dict["umount_directories"]:
        if tools.is_mount(os.path.join(config.BASE_DIRECTORY, d)):
            cmd = "umount -v $LFS/{d}".format(d=d)
            tools.add_to_dictionary(component_data_dict, key="post", value=cmd)

    # Generate 'umount' command from 'config.BASE_DIRECTORY'
    if tools.is_mount(config.BASE_DIRECTORY):
        cmd = "umount -v $LFS"
        tools.add_to_dictionary(component_data_dict, key="post", value=cmd)


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
