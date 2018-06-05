
import os
import sys

import config
import tools

def set_attributes(component_data_dict, parent_function):

    # Call parent_function
    parent_function()

    # Add the 'mount' command
    sources_orig = config.SOURCES_ORIG_DIRECTORY.replace(
        "@@LFSBUILDER_SRC_DIRECTORY@@",
        component_data_dict["lfsbuilder_src_directory"]
    )

    if tools.is_mount(os.path.join(config.BASE_DIRECTORY, "sources")) is False:
        # If 'sources' is not already mounted
        post_value = """mkdir -pv $LFS/sources
mount -v --bind {orig} $LFS/sources"""

        post_value = post_value.format(orig=sources_orig)

        # Add mount command to 'post' steps
        tools.add_to_dictionary(component_data_dict, key="post", value=post_value, concat=False)

    else:
        # Set 'post' to 'None'
        tools.add_to_dictionary(component_data_dict, key="post", value=None, concat=False)


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
