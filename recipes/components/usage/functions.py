import tools

def set_attributes(component_recipe_data, parent_function):

    parent_function()

    # Add the 'create_etc_sysconfig_console' parameter to 'post' steps.
    tools.add_to_dictionary(
        component_recipe_data,
        "post",
        component_recipe_data["create_etc_sysconfig_console"]
    )

