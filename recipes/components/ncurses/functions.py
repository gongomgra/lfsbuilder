
import os
import sys

import config
import tools
import printer

def run_post_steps(component_data_dict, parent_function):
    if component_data_dict["builder_name"] == "toolchain":
        parent_function()
    else:
        # If we are building 'system' we have to avoid running this. It tries to compile
        # component twice
        printer.warning("Skipped 'post' steps to avoid building component twice")
