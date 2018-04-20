
import os
import sys

import config
import tools

def modify_xml(componentfile_path):

    substitution_list = ["../bin/systemctl",
                         "/bin/systemctl",

                         "../lib/systemd/systemd",
                         "/lib/systemd/systemd"]

    tools.substitute_multiple_in_file(componentfile_path, substitution_list)


def set_attributes(component_data_dict, parent_function):
    # Call parent_function
    parent_function()

    # Prepend setting 'LC_ALL' to 'en_US.UTF-8' to the 'configure' step
    # so we ensure the rest of the commands run properly
    configure_cmd = """LC_ALL="en_US.UTF-8"
export LC_ALL

{c}""".format(c=component_data_dict["configure"])

    tools.add_to_dictionary(component_data_dict, "configure", configure_cmd, concat=False)
