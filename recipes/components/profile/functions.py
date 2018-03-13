
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):
    # 'profile' component creates '/etc/profile' and we have
    # to customize it
    tools.backup_file(componentfile_path)

    substitution_list = ["<replaceable>&lt;ll&gt;_&lt;CC&gt;.&lt;charmap&gt;&lt;@modifiers&gt;</replaceable>",
                         config.LANG]


    # Disable commands list
    disable_commands_list = ["LC_ALL=<replaceable>&lt;locale name&gt;</replaceable> locale charmap",
                             "LC_ALL=&lt;locale name&gt; locale language"]


    # Add commands that have been disabled to the 'subsitution_list'
    substitution_list.extend(tools.disable_commands(disable_commands_list))

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)
