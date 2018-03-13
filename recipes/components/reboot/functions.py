
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):
    # 'reboot' component runs command that we do not need.
    # We have to remove them.
    tools.backup_file(componentfile_path)

    substitution_list = []

    disable_commands_list = ["logout",
                             "shutdown -r now"]

    # Add commands that have been disabled to the 'subsitution_list'
    substitution_list.extend(tools.disable_commands(disable_commands_list))

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)


def set_attributes(component_data_dict, parent_function):

    # Call parent function
    parent_function()

    # Run component from the 'lfsbuilder_tmp_directory'
    tools.add_to_dictionary(component_data_dict,
                            key="build_directory_path",
                            value=component_data_dict["lfsbuilder_tmp_directory"],
                            concat=False)

    tools.add_to_dictionary(component_data_dict,
                            key="extracted_directory",
                            value=component_data_dict["lfsbuilder_tmp_directory"],
                            concat=False)
