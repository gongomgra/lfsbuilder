
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):

    # 'shadow' includes commands that set the 'root' user password interactively
    # during the 'system' step in chapter06.
    # We substitute this command for 'chpasswd' so we can set it in batch mode
    tools.backup_file(componentfile_path)

    substitution_list = ["<userinput>passwd root",
                         "<userinput remap=\"post\">echo \"root:{p}\" | chpasswd".format(
                             p=config.ROOT_PASSWD)]

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)
