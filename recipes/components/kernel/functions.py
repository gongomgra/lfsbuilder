
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):
    # 'kernel' component runs commands that we do not need. We have
    # to remove them
    tools.backup_file(componentfile_path)
    substitution_list = []

    disable_commands_list = ["make menuconfig",
                             "mount --bind /boot /mnt/lfs/boot"]

    # Add commands that have been disabled to the 'subsitution_list'
    substitution_list.extend(tools.disable_commands(disable_commands_list))

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)


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
