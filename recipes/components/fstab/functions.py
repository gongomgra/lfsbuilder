
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):
    # 'fstab' component creates '/etc/fstab' and we have
    # to customize it
    tools.backup_file(componentfile_path)

    substitution_list = ["<replaceable>&lt;xxx&gt;</replaceable>",
                         config.ROOT_PARTITION_NAME,

                         "<replaceable>&lt;fff&gt;</replaceable>",
                         config.FILESYSTEM_PARTITION_TYPE,

                         "<replaceable>&lt;yyy&gt;</replaceable>",
                         config.SWAP_PARTITION_NAME]

    disable_commands_list = ["<userinput>hdparm -I /dev/sda | grep NCQ"]

    # Add commands that have been disabled to the 'subsitution_list'
    disabled = tools.disable_commands(disable_commands_list)
    substitution_list.extend(disabled)


    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)
