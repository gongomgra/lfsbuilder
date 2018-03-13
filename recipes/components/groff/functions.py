
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):
    # 'groff' includes commands that are not necessary in the 'system' step chapter06
    # We remap them to 'notRequired' to avoid it to be included in '_post' steps
    tools.backup_file(componentfile_path)
    substitution_list = ["<replaceable>&lt;paper_size&gt;</replaceable>",
                         config.PAPER_SIZE]
    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)
