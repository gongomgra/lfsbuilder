
import os
import sys

import config
import tools
import printer

def set_attributes(builder_data_dict, parent_function):

    # Remove unnecessary components
    if config.INCLUDE_MESON_BUILD_SYSTEM is False:
        tools.remove_elements(builder_data_dict["components_to_build"],
                              builder_data_dict["meson_components"])
