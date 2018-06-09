
import os
import shutil
import config

def run_post_steps(component_data_dict, parent_function):

    # Run parent function
    parent_function()

    # Delete 'config.BASE_DIRECTORY/tools' if 'config.DELETE_TOOLS' is 'True'
    # Once the 'system' builder is built entirely, the toolchain is no longer
    # needed.
    directory = os.path.abspath(
        os.path.join(
            config.BASE_DIRECTORY,
            "tools"
        )
    )

    # Delete if exists and required
    if os.path.exists(directory) is True and config.DELETE_TOOLS is True:
        msg = "Deleting directory '{d}' because 'config.DELETE_TOOLS' is set to 'True'"
        msg = msg.format(d=directory)
        shutil.rmtree(directory)

