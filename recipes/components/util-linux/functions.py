
import os
import sys

import config
import tools

def modify_xml(componentfile_path):
    # Disable commands
    disable_commands_list = ["bash tests/run.sh --srcdir=$PWD --builddir=$PWD"]
    substitution_list = tools.disable_commands(disable_commands_list)

    tools.substitute_multiple_in_file(file_path, substitution_list)

def set_attributes(component_data_dict, parent_function):
    # Call parent_function
    parent_function()

    # Include tests for 'system' step to avoid issues running 'post.sh'
    if component_data_dict["builder_name"] == "system":
        component_data_dict["include_tests"] = True
