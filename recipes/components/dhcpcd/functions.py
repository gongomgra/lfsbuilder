import os
import sys

import config
import tools

def modify_xmlfile(component_recipe_data, componentfile_path, parent_function):

    parent_function(component_recipe_data, componentfile_path)

    disable_commands_list = ["""cat &gt; /etc/sysconfig/ifconfig.eth0 &lt;&lt; \"EOF\"
ONBOOT=\"yes\"
IFACE=\"eth0\"
SERVICE=\"dhcpcd\"
DHCP_START=\"-b -q -S ip_address=192.168.0.10/24 -S routers=192.168.0.1\"
DHCP_STOP=\"-k\"
EOF"""]

    aux_list = tools.disable_commands(disable_commands_list)
    tools.substitute_multiple_in_file(componentfile_path, aux_list)
