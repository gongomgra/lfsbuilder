
import os
import sys

import config
import tools
import printer

def get_components_to_build_list(builder_data_dict, parent_function):

    # Call parent function
    parent_function()

    # Remove unnecessary components
    if builder_data_dict["components_to_build"] is not None:
        if config.INCLUDE_MESON_BUILDER is False:
            tools.remove_elements(builder_data_dict["components_to_build"],
                                  builder_data_dict["meson_components"])

        if config.EXCLUDED_BOOT_MANAGER.lower() == "sysv":
            tools.remove_elements(builder_data_dict["components_to_build"],
                                  builder_data_dict["sysv_components"])

        elif config.EXCLUDED_BOOT_MANAGER.lower() == "systemd":
            tools.remove_elements(builder_data_dict["components_to_build"],
                                  builder_data_dict["systemd_components"])

        else:
            printer.error("Unknown boot manager '{b}' selected".format(b=config.BOOT_MANAGER))
