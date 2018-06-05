
import config

def get_components_to_build_list(builder_data_dict, parent_function):
    # Because 'blfs' include component 'createuser' to create 'config.NON_PRIVILEGED_USERNAME'
    # into the LFS sytem and this component is not present in the BLFS book,
    # we temporarily set 'config.CUSTOM_COMPONENTS_TO_BUILD' to 'True', run 'parent_function',
    # and restore its original value. This also allow us to keep using 'continue-at'.

    # .- get current value
    original_value = config.CUSTOM_COMPONENTS_TO_BUILD

    # .- set True
    setattr(config, "CUSTOM_COMPONENTS_TO_BUILD", True)

    # .- run 'parent_function'
    parent_function()

    # .- restore original value
    setattr(config, "CUSTOM_COMPONENTS_TO_BUILD", original_value)
