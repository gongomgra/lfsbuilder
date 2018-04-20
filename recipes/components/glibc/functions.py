
import os
import sys

import config
import tools

def modify_xmlfile(componentfile_path):
    # 'glibc' includes commands that are not necessary in the 'system' step (chapter06)
    # We remap them to 'notRequired' to avoid it to be included in '_post' steps
    tools.backup_file(componentfile_path)
    substitution_list = ["<replaceable>&lt;xxx&gt;</replaceable>",
                         config.TIMEZONE]
# "@@LFS_TIMEZONE@@"]

    disable_commands_list = ["tzselect"]

    # Add commands that have been disabled to the 'substitution_list'
    disabled = tools.disable_commands(disable_commands_list)
    substitution_list.extend(disabled)

    # Substitute
    tools.substitute_multiple_in_file(componentfile_path, substitution_list)


def set_attributes(component_data_dict, parent_function):
    if component_data_dict["builder_name"] == "system":
        # component_data_dict["component_substitution_list"] = ["@@LFS_TIMEZONE@@", config.TIMEZONE]

        # Custom 'localedef' command for users to add their own
        cmd = "localedef -i {locale} -f {charmap} {lang}".format(locale = config.LOCALE,
                                                                 charmap = config.CHARMAP,
                                                                 lang = config.LANG)
        tools.add_to_dictionary(component_data_dict, "post", cmd)


        # Run 'previous' steps into 'compile.sh' file for 'system' builder.
        # It sets the 'GCC_INCDIR' variable that is required for 'configure' step
        if component_data_dict["builder_name"] == "system":
            configure_cmd = """{p}
{c}""".format(p=component_data_dict["previous"], c=component_data_dict["configure"])

            tools.add_to_dictionary(component_data_dict, "configure", configure_cmd, concat=False)


        # Compilation check
        # if self.builder_name == "toolchain":
        #     self.check_cc_command = "$LFS_TGT-gcc dummy.c"
        #     self.check_grep_command = "readelf -l a.out | grep ': /tools'"
        #     self.check_rm_command = "rm -v dummy.c a.out"


        # Call parent function
        parent_function()

#def run_post_steps(component_data_dict, parent_function):
    # if component_data_dict["builder_name"] == "toolchain":
    #     self.check_compiling_and_linking_functions()

    #     # Call parent function
    #     parent_function()
#    pass
