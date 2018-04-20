
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):
    # 'consoled' component runs commands that we need to disable
    # We also need to customize the '/etc/vconsole.conf' file
    tools.backup_file(componentfile_path)

    substitution_list = ["KEYMAP=de-latin1",
                         "KEYMAP={km}".format(km=config.KEYMAP),

                         "FONT=Lat2-Terminus16",
                         "FONT={f}".format(f=config.CONSOLE_FONT)]

    disable_commands_list = ["localectl"]

    # Add commands that have been disabled to the 'subsitution_list'
    substitution_list.extend(tools.disable_commands(disable_commands_list))

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)
