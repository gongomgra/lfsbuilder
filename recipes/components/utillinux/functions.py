
import os
import sys

import config
import tools

def set_attributes(component_data_dict, parent_function):
    # Include tests for 'system' step to avoid issues running 'post.sh'
    if component_data_dict["builder_name"] == "system":
        component_data_dict["include_tests"] = True

    # Call parent_function
    parent_function()
