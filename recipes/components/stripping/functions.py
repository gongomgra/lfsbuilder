
import os
import sys

import config
import tools

# def modify_xmlfile(componentfile_path):
#     # 'strippingagain' includes commands that are not necessary for us.
#     # We will remap them to 'notRequired'
#     # to avoid them to be included in '_post' step
#     if os.path.basename(componentfile_path) == "strippingagain.xml":
#         tools.backup_file(componentfile_path)
#         tools.substitute_in_file(componentfile_path,
#                                  "<screen role=\"nodump\"><userinput>",
#                                  "<screen role=\"nodump\"><userinput remap=\"notRequired\">")


def set_attributes(component_data_dict, parent_function):

#     if component_data_dict["builder_name"] == "system":
#         component_data_dict["key_name"] = "strippingagain"

#     # Modify keys that match the 'key_name', if any
#     for key, value in component_data_dict.items():
#         if key.startswith(component_data_dict["key_name"]):
#             # Rename 'component named' keys removing the 'component_name' and add to dictionary
#             new_key = key.replace("{c}_".format(c=component_data_dict["key_name"]),
#                                   "")
#             tools.add_to_dictionary(component_data_dict, new_key, value, concat=False)



    # According to the link below, not all files can be stripped, so we ignore those errors
    # http://archives.linuxfromscratch.org/mail-archives/lfs-support/2002-July/008317.html
    new_value = component_data_dict["post"].replace("/tools/lib/*", "/tools/lib/* || true").replace("/tools/{,s}bin/*", "/tools/{,s}bin/* || true")
    tools.add_to_dictionary(component_data_dict, "post", new_value, concat=False)

    # Call parent method
    parent_function()
