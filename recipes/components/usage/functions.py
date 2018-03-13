
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):
    # 'usage' component runs commands that we do not need. We have
    # to remove them. Also we have to modify the 'grub.cfg' file
    tools.backup_file(componentfile_path)

    substitution_list = []

    disable_commands_list = ["cat &gt; /etc/sysconfig/console &lt;&lt; \"EOF\""]

    # Add commands that have been disabled to the 'subsitution_list'
    substitution_list.extend(tools.disable_commands(disable_commands_list))

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)
