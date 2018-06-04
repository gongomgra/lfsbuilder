import os
import sys

import config
import tools
import printer

def run_post_steps(component_data_dict, parent_function):

    parent_function()

    printer.substep_info("Installing provided ssh public key")
    filename = os.path.join(component_data_dict["lfsbuilder_src_directory"],
                            "recipes",
                            "components",
                            "openssh",
                            "files",
                            component_data_dict["openssh_public_key_filename"])

    tools.copy_file(filename,
                    os.path.join(component_data_dict["extracted_directory"], ".config"))
