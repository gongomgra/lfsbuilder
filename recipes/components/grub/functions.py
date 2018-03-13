
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):
    # 'grub' component runs commands that we do not need. We have
    # to remove them. Also we have to modify the 'grub.cfg' file
    tools.backup_file(componentfile_path)

    substitution_list = ["<userinput>grub-install /dev/sda</userinput>",
                         "<userinput>grub-install --no-floppy --force \
--root-directory={bd} /dev/{grpn}</userinput>".format(bd=config.BASE_DIRECTORY,
                                                      grpn=config.GRUB_ROOT_PARTITION_NAME),

                         "cat &gt; /boot",
                         "cat &gt; {bd}/boot".format(bd=config.BASE_DIRECTORY),

                         "set root=(hd0,2)",
                         "set root=({grpnu})".format(grpnu=config.GRUB_ROOT_PARTITION_NUMBER),

                         "root=/dev/sda2",
                         "root=/dev/{rpn}".format(rpn=config.ROOT_PARTITION_NAME)]

    disable_commands_list = ["cd /tmp"]

    # Add commands that have been disabled to the 'subsitution_list'
    disabled = tools.disable_commands(disable_commands_list)
    substitution_list.extend(disabled)

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)


def set_attributes(component_data_dict, parent_function):

    # Call parent_function
    parent_function()

    if component_data_dict["builder_name"] == "configuration":
        # Build this component from outside the chroot
        tools.add_to_dictionary(component_data_dict, key="build_into_chroot", value=False, concat=False)
        tools.add_to_dictionary(component_data_dict, key="run_as_username", value="root", concat=False)
