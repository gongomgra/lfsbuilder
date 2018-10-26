
import os
import sys

import config
import tools

def set_attributes(component_data_dict, parent_function):

    # Call parent function
    parent_function()

    if component_data_dict["builder_name"] == "system":
        # Custom 'localedef' command for users to add their own
        cmd = "localedef -i {locale} -f {charmap} {lang}".format(locale = config.LOCALE,
                                                                 charmap = config.CHARMAP,
                                                                 lang = config.LANG)
        tools.add_to_dictionary(component_data_dict, "post", cmd)


        # Run 'previous' steps into 'compile.sh' file for 'system' builder.
        # Starting on version 8.2 it sets the 'GCC_INCDIR' variable
        # which is required for 'configure' step
        if component_data_dict["builder_name"] == "system" and float(config.LFS_VERSION) >= 8.2:
            configure_cmd = """{p}
{c}""".format(p=component_data_dict["previous"], c=component_data_dict["configure"])

            tools.add_to_dictionary(component_data_dict, "configure", configure_cmd, concat=False)

            # Set 'previous' to None so it is not executed twice
            tools.add_to_dictionary(component_data_dict, "previous", None, concat=False)
