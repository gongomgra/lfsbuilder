import tools

def modify_xmlfile(component_recipe_data, componentfile_path, parent_function):
    # Disable 'site' entity that points to non existent file and fails
    disable_site_entity = ['<!ENTITY site               SYSTEM "../appendices/rc.site.script">',
                           '<!-- <!ENTITY site               SYSTEM "../appendices/rc.site.script"> -->',
                           '<screen role="auto">&site;</screen>',
                           '<!-- <screen role="auto">&site;</screen> -->']

    component_recipe_data["component_substitution_list"].extend(disable_site_entity)

    # call parent_method
    parent_function(component_recipe_data, componentfile_path)


def set_attributes(component_recipe_data, parent_function):

    parent_function()

    # Add the 'create_etc_sysconfig_console' parameter to 'post' steps.
    tools.add_to_dictionary(
        component_recipe_data,
        "post",
        component_recipe_data["create_etc_sysconfig_console"]
    )

