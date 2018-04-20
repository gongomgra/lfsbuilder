
import os
import sys

import config
import tools
import printer

def set_attributes(builder_data_dict, parent_function):

    # Call parent function
    parent_function()

    # We remove the 'reboot' component because it will fail
    # when umounting the 'BASE_DIRECTORY' because it is in use (the 'setenv.sh' file).
    # The left the 'umount' component to do the work later within the 'collector' builder.
    tools.remove_element(builder_data_dict["components_to_build"],
                         "reboot")

    # Remove unnecessary components depending on the 'boot manager' selected
    if config.EXCLUDED_BOOT_MANAGER.lower() == "sysv":
        tools.remove_elements(builder_data_dict["components_to_build"],
                              builder_data_dict["systemd_components"])

    elif config.EXCLUDED_BOOT_MANAGER.lower() == "systemd":
        tools.remove_elements(builder_data_dict["components_to_build"],
                              builder_data_dict["sysv_components"])

    else:
        printer.error("Unknown boot manager '{b}' selected".format(b=config.EXCLUDED_BOOT_MANAGER))
