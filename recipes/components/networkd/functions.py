
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):
    # 'network' component create '/etc/sysconfig/ifconfig.eth0' and
    # '/etc/resolv.conf' files that we have to customize it
    tools.backup_file(componentfile_path)

    substitution_list = ["Address=192.168.0.2/24",
                         "IP={eth0_ip}/{eth0_mask}".format(eth0_ip=config.ETH0_IP_ADDRESS,
                                                           eth0_mask=config.ETH0_MASK),

                         "Gateway=192.168.0.1",
                         "Gateway={eth0_gateway}".format(eth0_gateway=config.ETH0_GATEWAY_ADDRESS),

                         "DNS=192.168.0.1",
                         "DNS={eth0_dns}".format(eth0_dns=config.DNS_ADDRESS_1),

                         "<replaceable>&lt;Your Domain Name&gt;</replaceable>",
                         config.DOMAIN_NAME,

                         "<replaceable>&lt;IP address of your primary nameserver&gt;</replaceable>",
                         config.DNS_ADDRESS_1,

                         "<replaceable>&lt;IP address of your secondary nameserver&gt;</replaceable>",
                         config.DNS_ADDRESS_2,

                         "<replaceable>&lt;lfs&gt;</replaceable>",
                         config.HOSTNAME,

                         "<replaceable>&lt;192.168.1.1&gt;</replaceable>",
                         config.ETH0_IP_ADDRESS,

                         "<replaceable>&lt;HOSTNAME.example.org&gt;</replaceable>",
                         "{hostname}.example.com".format(hostname=config.HOSTNAME),

                         "<replaceable>[alias1] [alias2 ...]</replaceable>",
                         ""]

    # Disable commands list
    disable_commands_list = ["""<screen role=\"nodump\"><userinput>cat &gt; /etc/hosts &lt;&lt; \"EOF\"
# Begin /etc/hosts (no network card version)"""]

    # Add commands that have been disabled to the 'subsitution_list'
    substitution_list.extend(tools.disable_commands(disable_commands_list))

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)
