import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):

    tools.backup_file(componentfile_path)

    # Modify bootscript installation
    bootscript_install_cmd = "make install-sshd"
    new_command = tools.modify_blfs_component_bootscript_install(bootscript_install_cmd)

    substitution_list = [bootscript_install_cmd,
                         new_command]

    # Disable commands list
    disable_commands_list = ["ssh-keygen",
                             "sed 's@d/login@d/sshd@g' /etc/pam.d/"]

    # Add commands that have been disabled to the 'subsitution_list'
    substitution_list.extend(tools.disable_commands(disable_commands_list))

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)

def run_post_steps(component_data_dict, parent_function):

    parent_function()


    print("Installing provided ssh public key")
    filename = os.path.join(component_data_dict["lfsbuilder_src_directory"],
                            "recipes",
                            "components",
                            "openssh",
                            "files",
                            component_data_dict["openssh_public_key_filename"])

    tools.copy_file(filename,
                    os.path.join(component_data_dict["extracted_directory"], ".config"))
