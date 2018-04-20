
import os
import sys

import config
import tools
import printer

def set_attributes(builder_data_dict, parent_function):

    # .- Write 'setenv.sh' into 'lfs_src_directory/tmp'
    tools.add_to_dictionary(builder_data_dict,
                            "setenv_directory",
                            builder_data_dict["lfsbuilder_tmp_directory"],
                            concat=False)

    tools.add_to_dictionary(builder_data_dict,
                            "sources_directory",
                            builder_data_dict["lfsbuilder_tmp_directory"],
                            concat=False)


    # Call parent function
    parent_function()
