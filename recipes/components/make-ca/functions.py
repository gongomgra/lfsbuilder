
import os
import sys

import config
import tools

def modify_xmlfile(component_data_dict, component_filepath, parent_function):

    if (config.LFS_VERSION == '8.4'):
        # Disable MakeBelieve certificate commands
        component_data_dict['component_substitution_list'].extend(
            [
                r"""<screen role="nodump"><userinput>install -vdm755 /etc/ssl/local &amp;&amp;
openssl x509 -in /etc/ssl/certs/Makebelieve_CA_Root.pem""",
                r"""<screen role="nodump"><userinput remap="lfsbuilder_disabled">install -vdm755 /etc/ssl/local &amp;&amp;
openssl x509 -in /etc/ssl/certs/Makebelieve_CA_Root.pem"""
            ]
        )


    # Call parent_function
    parent_function(component_data_dict, component_filepath)


