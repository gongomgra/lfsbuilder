
import os
import sys

import config
import tools
import printer

def set_attributes(component_data_dict, parent_function):

    # LFS version 8.0 has a previous command error for 'sed-4.4'. We will add the correct one here
    # http://lfs-dev.linuxfromscratch.narkive.com/Qy0pWTSI/6-24-sed-4-4-test-failure
    value = component_data_dict["previous"]
    if value is not None:
        value = value.replace("sed -i 's/panic-tests.sh//' Makefile.in",
                              "sed -i 's/testsuite.panic-tests.sh//' Makefile.in")

    # Update value in dictionary
    tools.add_to_dictionary(component_data_dict, "previous", value, concat=False)

    # Call parent function
    parent_function()
