
import os
import sys
import argparse

import config
import tools
import printer

class ModifyBuildersList(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        # Sanitize builders list by converting elements to lowercase
        self.builders_list = [b.lower() for b in values]

        # .- Check there is not any duplicated builder before doing anything else
        self.check_builders_dupes()

        # Set 'config.REMOVE_REBOOT_COMPONENT' if 'configuration' is not the latest builder
        if self.builders_list[-1] != "configuration":
            setattr(config, "REMOVE_REBOOT_COMPONENT", True)

        # Modify builders list by adding 'provider' and
        # 'collectors' builders

        # .- Remove 'provider' if present and ensure it is placed
        # at the beginning of the 'self.builders_list'
        tools.remove_all_and_add_element(self.builders_list, "provider", index=0)

        # .- Remove 'collector' if present and ensure it is placed
        # at the end of the 'self.builders_list'
        tools.remove_all_and_add_element(self.builders_list, "collector")

        # Substitute 'lfs' name for its builders component
        tools.substitute_in_list(self.builders_list, "lfs", ["toolchain", "system", "configuration"])


        # .- Check there is not any duplicated builder after substitutions. Raise error if so
        self.check_builders_dupes()

        # .- Check we are not trying to run 'blfs' before any 'lfs' component
        self.check_builders_order()

        # Set generated value. 'self.dest' is the argument name 'builders_list'
        setattr(namespace, self.dest, self.builders_list)


    def check_builders_dupes(self, bl=None):
        # We are running this method from 'unittest'
        if bl is not None:
            self.builders_list = bl

        for b in set(self.builders_list):
            if self.builders_list.count(b) > 1:
                printer.error("Duplicated builder '{b}' is not allowed".format(b=b))


    def check_builders_order(self, bl=None):
        # We are running this method from 'unittest'
        if bl is not None:
            self.builders_list = bl

        # Get the position number of every builder into the 'self.builders_list'
        self.builders_index_dict = {"toolchain": tools.get_element_index(self.builders_list,
                                                                         "toolchain",
                                                                         not_present=-2),

                                    "system": tools.get_element_index(self.builders_list,
                                                                      "system",
                                                                      not_present=-2),

                                    "configuration": tools.get_element_index(self.builders_list,
                                                                             "configuration",
                                                                             not_present=-2),

                                    "blfs": tools.get_element_index(self.builders_list,
                                                                    "blfs",
                                                                    not_present=-1)
        }

        # .- Ensure 'blfs' is present and its 'index' is max
        if self.builders_index_dict["blfs"] != -1 and \
           self.builders_index_dict["blfs"] != max(self.builders_index_dict.values()):
            printer.error("You can not build 'blfs' before any of the 'lfs' book's builders")

        # .- Check present 'lfs' book's builders can be built
        is_toolchain_present = tools.is_element_present(self.builders_list, "toolchain")
        is_system_present = tools.is_element_present(self.builders_list, "system")
        is_configuration_present = tools.is_element_present(self.builders_list, "configuration")


        has_toolchain_min_index = self.builders_index_dict["toolchain"] == min([
            self.builders_index_dict["toolchain"],
            self.builders_index_dict["system"],
            self.builders_index_dict["configuration"]
        ])
        # Would be equal only in case both are not present
        is_system_before_configuration = self.builders_index_dict["system"] <= self.builders_index_dict["configuration"]

        is_lfs_order_valid = self.check_lfs_builders_order(t = is_toolchain_present,
                                                           s = is_system_present,
                                                           c = is_configuration_present,
                                                           m = has_toolchain_min_index,
                                                           l = is_system_before_configuration)

        # .- Check provided 'lfs' book's builder order
        if is_lfs_order_valid is False:
            printer.error("You are trying to build 'lfs' book's builders in a wrong order")



    def check_lfs_builders_tuple(self, t, s, c):
        """
        This function checks if provided 'lfs' book's builders combination
is valid (order doesn't matter) by implementing solution for the below Karnaugh map

  \ sc
t  \   00   01   10   11
    +____________________+
0   |  1  | 1  | 1  | 1  |
    +-----+----+----+----+
1   |  1  | 0  | 1  | 1  |
    +-----+----+----+----+

"""
        return (not(t)) or s or (not(c))


    def check_lfs_builders_order(self, t, s, c, m, l):
        """
        This function checks if provided 'lfs' book's builders combination
is valid (order does matter) by implementing solution for the corresponding
5 variable's Karnaugh map where inputs are

t: whether the 'toolchain' builder is pretended to be built or not

s: whether the 'system' builder is pretended to be built or not

c: whether the 'configuration' builder is pretended to be built or not

m: whether the 'toolchain' builder is pretended to be built first or not. That's it,
   if its index value is the minimum between them.

l: whether the 'system' builder is pretended to be built before the 'configuration' builder or not.
   That's true if its index value is the minimum between them.

"""
        # Ensure we are getting boolean values as input
        t = bool(t)
        s = bool(s)
        c = bool(c)
        m = bool(m)
        l = bool(l)

        return (not(t) and l) or \
            (not(s) and not(c)) or \
            (not(t) and not(c)) or \
            (not(t) and not(s) and m) or \
            (not(t) and not(s) and not(m)) or \
            (s and m and l) or \
            (not(c) and m)


class SetConfigOption(argparse.Action):

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(config, self.dest.upper(), value)
