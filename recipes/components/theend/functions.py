
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):
    # 'theend' component creates '/etc/lsb-release' file that
    # we have to customize.
    tools.backup_file(componentfile_path)

    substitution_list = ["DISTRIB_ID=\"Linux From Scratch\"",
                         "DISTRIB_ID=\"{dn}\"".format(dn=config.DISTRIBUTION_NAME),

                         "DISTRIB_RELEASE=\"&version;\"",
                         "DISTRIB_RELEASE=\"{dv}\"".format(dv=config.DISTRIBUTION_VERSION),

                         "DISTRIB_CODENAME=\"&lt;your name here&gt;\"",
                         "DISTRIB_CODENAME=\"{dn}\"".format(dn=config.DISTRIBUTION_NAME),

                         "DISTRIB_DESCRIPTION=\"Linux From Scratch\"",
                         "DISTRIB_DESCRIPTION=\"{dd}\"".format(dd=config.DISTRIBUTION_DESCRIPTION)]

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)


# def set_attributes(component_data_dict, parent_function):

#     parent_function()

#     component_data_dict["component_substitution_list"] = [
#         "@@LFS_DISTRIBUTION_NAME@@", config.DISTRIBUTION_NAME,
#         "@@LFS_DISTRIBUTION_VERSION@@", config.DISTRIBUTION_VERSION,
#         "@@LFS_DISTRIBUTION_DESCRIPTION@@", config.DISTRIBUTION_DESCRIPTION]
