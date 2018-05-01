
import os
import sys

import config
import tools

def set_attributes(component_data_dict, parent_function):
    # Call parent function
    parent_function()

    # Required patch for glibc to compile properly. Add it to gcc2 previous steps
    # http://stackoverflow.com/questions/15787684/lfs-glibc-compilation-ld-error
    tools.add_to_dictionary(component_data_dict,
                            "previous",
                            "sed -i '/k prot/agcc_cv_libc_provides_ssp=yes' gcc/configure")
    tools.add_to_dictionary(component_data_dict,
                            "previous",
                            "sed -i 's/if \((code.*))\)/if (\&1; \&\& \!DEBUG_INSN_P (insn))/' gcc/sched-deps.c")
