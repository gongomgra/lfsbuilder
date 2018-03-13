
import os
import sys

import config
import tools

def set_attributes(component_data_dict, parent_function):

    # Required patch for glibc to compile properly. Add it to gcc previous steps
    # http://stackoverflow.com/questions/15787684/lfs-glibc-compilation-ld-error
    tools.add_to_dictionary(component_data_dict,
                            "previous",
                            "sed -i '/k prot/agcc_cv_libc_provides_ssp=yes' gcc/configure")
    tools.add_to_dictionary(component_data_dict,
                            "previous",
                            "sed -i 's/if \((code.*))\)/if (\&1; \&\& \!DEBUG_INSN_P (insn))/' gcc/sched-deps.c")


    # Run parent_function
    parent_function()

def run_previous_steps(component_data_dict, parent_function):
    # Run parent function
    parent_function()

    if component_data_dict["builder_name"] == "toolchain":
        # Previous steps extract 'mpfr', 'gmp' and 'mpc' tarballs as 'root' user. We need to set owner.
        tools.set_recursive_owner_and_group(component_data_dict["extracted_directory"],
                                            component_data_dict["run_as_username"])


def run_post_steps(component_data_dict, parent_function):
    # if self.builder_name == "system":
    #     # Don't call parent function as the only check it includes in 'post' is already here
    #     self.check_compiling_and_linking_functions()
    # else:
    #     # Call parent function
    #     parent_function()
    pass
