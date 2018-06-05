

import tools


def set_attributes(component_data_dict, parent_function):
    # Call parent_function
    parent_function()

    # Include tests for 'system' step to avoid issues running 'post.sh'
    if component_data_dict["builder_name"] == "system":
        tools.add_to_dictionary(
            component_data_dict,
            "include_tests",
            True,
            concat=False
        )

