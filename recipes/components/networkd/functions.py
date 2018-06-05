
import os
import sys

import config
import tools

def modify_xmlfile(component_recipe_data, componentfile_path, parent_function):

    # Update 'disable_commands_list' depending of 'resolvconf_method'
    if component_recipe_data["resolvconf_method"] == "static":
        component_recipe_data["disable_commands_list"].append(
            component_recipe_data["resolvconf_symlink_command"]
        )
    elif component_recipe_data["resolvconf_method"] == "symlink":
        component_recipe_data["disable_commands_list"].append(
            component_recipe_data["resolvconf_static_command"]
        )
    else:
        # Disable 'symlink' command by default
        component_recipe_data["disable_commands_list"].append(
            component_recipe_data["resolvconf_symlink_command"]
        )

    # call parent_method
    parent_function(component_recipe_data, componentfile_path)
