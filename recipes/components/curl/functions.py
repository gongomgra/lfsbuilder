import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):

    # 'curl' xml files run commands using logic conditions.
    # That is: patch && configure && make
    # We are applying patches in a previous step, so 'configure' never
    # run because the 'patch' commands return 'FALSE' and the conditional statement
    # ends in that point: patch && configure && make --> 0 && configure && make
    # We enforce to return 'TRUE' to fix it
    tools.backup_file(componentfile_path)
    substitution_list = [".patch &amp;&amp;",
                         ".patch || true"]

    tools.substitute_multiple_in_file(componentfile_path, substitution_list)
