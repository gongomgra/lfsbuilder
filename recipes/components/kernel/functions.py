
import os
import sys

import config
import tools

def run_previous_steps(component_data_dict, parent_function):

    # Call parent function
    parent_function()

    print("Copying custom \'.config\' file")
    filename = os.path.join(component_data_dict["lfsbuilder_src_directory"],
                            "recipes",
                            "components",
                            "kernel",
                            "files",
                            component_data_dict["kernel_config_filename"])

    tools.copy_file(filename,
                    os.path.join(component_data_dict["extracted_directory"], ".config"))
