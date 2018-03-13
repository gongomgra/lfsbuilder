
import os
import sys

import config
import tools

def set_attributes(component_data_dict, parent_function):

    # Call parent_function
    parent_function()

    # Command to generate img
    post_text = """
echo "Running 'dd' command. This may take a while..."
dd if=/dev/zero of=@@LFS_IMG_FILENAME@@ bs=1 count=@@LFS_IMG_SIZE@@

"""
    post_text = post_text.replace("@@LFS_IMG_FILENAME@@", config.IMG_FILENAME)
    post_text = post_text.replace("@@LFS_IMG_SIZE@@", config.IMG_SIZE)

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
