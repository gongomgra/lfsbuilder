import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):


    tools.backup_file(componentfile_path)

    # Modify bootscript installation
    bootscript_install_cmd = "make install-service-dhcpcd"
    new_command = tools.modify_blfs_component_bootscript_install(bootscript_install_cmd)

    substitution_list = [bootscript_install_cmd,
                         new_command,

                         "<replaceable>&lt;insert appropriate start options here&gt;</replaceable>",
                         "",

                         "<replaceable>&lt;insert additional stop options here&gt;</replaceable>",
                         ""]


    disable_commands_list = ["make install-dhcpcd",
                             "systemctl",
                             """cat &gt; /etc/sysconfig/ifconfig.eth0 &lt;&lt; \"EOF\"
<literal>ONBOOT=\"yes\"
IFACE=\"eth0\"
SERVICE=\"dhcpcd\"
DHCP_START=\"-b -q -S ip_address=192.168.0.10/24 -S routers=192.168.0.1\"
DHCP_STOP=\"-k\"</literal>
EOF"""]

    # Add commands that have been disabled to the 'subsitution_list'
    disabled = tools.disable_commands(disable_commands_list)
    substitution_list.extend(disabled)


    tools.substitute_multiple_in_file(componentfile_path, substitution_list)
