
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):

    # 'symlinks' component issue 'udevadm' commands that may fail and
    # according to the book it is not necessary to create those symlinks right now.
    # Because of that, we mark them as 'not-required'
    tools.backup_file(componentfile_path)

    substitution_list = []

    disable_commands_list = ["udevadm test /sys/block/hdd",
                             "sed -i -e 's/\"write_cd_rules\"/\"write_cd_rules",
                             "udevadm info -a -p /sys/class/video4linux/video0",
                             "cat &gt; /etc/udev/rules.d/83-duplicate_devs.rules"]

        # Add commands that have been disabled to the 'subsitution_list'
    substitution_list.extend(tools.disable_commands(disable_commands_list))

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)
