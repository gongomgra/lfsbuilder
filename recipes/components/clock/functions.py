
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):
    # 'clock' component runs commands that we need to disable
    tools.backup_file(componentfile_path)

    disable_commands_list = ["timedatectl", "systemctl disable systemd-timesyncd"]

    # Add commands that have been disabled to the 'subsitution_list'
    substitution_list = tools.disable_commands(disable_commands_list)

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)
