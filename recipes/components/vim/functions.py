
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):

    # 'vim' includes commands that are not necessary in the 'system' step chapter06
    # We remap them to 'notRequired' to avoid it to be included in '_post' steps
    tools.backup_file(componentfile_path)

    substitution_list = []

    disable_commands_list = ["vim -c \':options\'"]

    # Add commands that have been disabled to the 'subsitution_list'
    substitution_list.extend(tools.disable_commands(disable_commands_list))

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)
