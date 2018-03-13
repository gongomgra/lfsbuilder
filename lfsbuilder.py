#!/usr/bin/python

import os
import sys
import argparse

import builders
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


    def check_builders_dupes(self):
        for b in set(self.builders_list):
            if self.builders_list.count(b) > 1:
                printer.error("Duplicated builder '{b}' is not allowed".format(b=b))

    def check_builders_order(self):
        index_dict = {"toolchain": tools.get_element_index(self.builders_list,
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
        if index_dict["blfs"] != -1 and \
           index_dict["blfs"] != max(index_dict.values()):
            printer.error("You can not build 'blfs' before any of the 'lfs' book's builders")

        # .- Check present 'lfs' book's builders can be built
        is_toolchain_present = tools.is_element_present(self.builders_list, "toolchain")
        is_system_present = tools.is_element_present(self.builders_list, "system")
        is_configuration_present = tools.is_element_present(self.builders_list, "configuration")


        has_toolchain_min_index = index_dict["toolchain"] == min([index_dict["toolchain"],
                                                                  index_dict["system"],
                                                                  index_dict["configuration"]])
        # Would be equal only in case both are not present
        is_system_before_configuration = index_dict["system"] <= index_dict["configuration"]

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

        return (not(t) and l) or (not(s) and not(c)) or (not(t) and not(c)) or (not(t) and not(s) and m) or (not(t) and not(s) and not(m)) or (s and m and l) or (not(c) and m)


class SetConfigOption(argparse.Action):

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(config, self.dest.upper(), value)


class LFSBuilder(object):

    def __init__ (self):
        self.lfsbuilder_src_directory = os.path.dirname(os.path.realpath(__file__))
        self.temporal_folder = os.path.join(self.lfsbuilder_src_directory, "tmp")

        # Parse command line
        self.parser = argparse.ArgumentParser(
            description = "LFSBuilder")
#             usage = """lfsbuilder.py [<options>] <command> [<args>]
# Options:


# Commands:
#   build     Build specified builders
#   parse     Generate XML commands file for specified builder
#   download  Download
# """)

        # Arguments definition
        # .- verbose
        self.parser.add_argument("-v", "--verbose",
                                 help="Output verbose messages",
                                 action="store_true")


        # .- base directory
        self.parser.add_argument("--base-directory",
                                 help="Set base directory",
                                 action=SetConfigOption)

        # .- non privileged username
        self.parser.add_argument("--non-privileged-username",
                                 help="Set non privileged username",
                                 action=SetConfigOption)

        # .- sources orig directory
        self.parser.add_argument("--sources-orig-directory",
                                 help="Set origin directory for sources",
                                 action=SetConfigOption)

        # .- makeflags
        self.parser.add_argument("--makeflags",
                                 help="Set MAKEFLAGS value",
                                 action=SetConfigOption)

        # .- restore XML backups file
        self.parser.add_argument("--restore-xml-backups",
                                 help="Restore XML backups files",
                                 action=SetConfigOption)

        # .- timezone
        self.parser.add_argument("--lfs-version",
                                 help="Version of the book",
                                 action=SetConfigOption)

        # .- command. Save all the arguments starting from the command name until
        # the end of the 'argv' values into a list
        self.parser.add_argument("command",
                                 help="Subcommand to run",
                                 nargs=argparse.REMAINDER)


        # Parse sys.args and use dispatcher pattern to
        # invoke method named as command
        self.all_args = self.parser.parse_args()

        # Set boolean configuration flags
        self.set_config_option(self.all_args)

        if not hasattr(self, self.all_args.command[0]):
            printer.warning("Unknown command '{c}'".format(c=self.all_args.command[0]))
            # self.parser.print_help()
            sys.exit(1)

        # Run command
        getattr(self, self.all_args.command[0])()


    def build(self):
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description = "Build specified builders",
            usage = "Usage for build")

        # Arguments definition
        # .- generate-img-file
        parser.add_argument("--generate-img-file",
                            action = "store_true")

        parser.add_argument("--no-generate-img-file",
                            action = "store_true")

        # .- no mount sources
        parser.add_argument("--mount-sources",
                            action = "store_true")

        parser.add_argument("--no-mount-sources",
                            action = "store_true")

        # .- mount-img-file
        parser.add_argument("--mount-img-file",
                            action = "store_true")

        parser.add_argument("--no-mount-img-file",
                            action = "store_true")

        # .- builders list
        parser.add_argument("builders_list",
                            action=ModifyBuildersList,
                            nargs=argparse.REMAINDER)

        # .- mount-system-directories
        parser.add_argument("--mount-system-directories",
                            action = "store_true")

        parser.add_argument("--no-mount-system-directories",
                            action = "store_true")


        # Parse arguments
        self.build_args = parser.parse_args(self.all_args.command[1:])

        # Set boolean configuration flags
        self.set_config_option(self.build_args)

        # Create and build 'builders_list'

        # 1.- Create 'tmp' directory
        tools.create_directory(self.temporal_folder)

        for builder in self.build_args.builders_list:
            os.chdir(self.lfsbuilder_src_directory)
            # Generate builder object from BuilderGenerator
            bg = builders.BuilderGenerator(builder)
            o = bg.get_builder_reference()
            del bg

            # Run the real builder
            o.set_attributes()

            # Generate commands file if necessary
            o.generate_commands_file()

            o.build()
            o.clean_workspace()
            del o
            print "---"



    def set_config_option(self, flags):

        tools.pretty_print(flags)

        # .- Set 'verbose' if 'True'
        if "verbose" in flags and flags.verbose is True:
            print "Setting 'verbose'"
            setattr(config, "VERBOSE", True)

        # .- Set 'generate_img_file' if 'True'
        if "no_generate_img_file" in flags and flags.no_generate_img_file is True:
            setattr(config, "GENERATE_IMG_FILE", False)

        if "generate_img_file" in flags and flags.generate_img_file is True:
            setattr(config, "GENERATE_IMG_FILE", True)

        # .- Set 'mount_img_file'
        if "no_mount_img_file" in flags and flags.no_mount_img_file is True:
            setattr(config, "MOUNT_IMG_FILE", False)

        if "mount_img_file" in flags and flags.mount_img_file is True:
            setattr(config, "MOUNT_IMG_FILE", True)

        # .- Set 'mount_sources_directory'
        if "no_mount_sources" in flags and flags.no_mount_sources is True:
            setattr(config, "MOUNT_SOURCES_DIRECTORY", False)

        if "mount_sources" in flags and flags.mount_sources is True:
            setattr(config, "MOUNT_SOURCES_DIRECTORY", True)

        # Set 'config.MOUNT_SYSTEM_BUILDER_DIRECTORIES'
        if "no_mount_system_directories" in flags and flags.no_mount_system_directories is True:
            setattr(config, "MOUNT_SOURCES_DIRECTORY", False)

        if "mount_system_directories" in flags and flags.mount_system_directories is True:
            setattr(config, "MOUNT_SYSTEM_BUILDER_DIRECTORIES", True)



if __name__ == '__main__':
    lfsb = LFSBuilder()
    del lfsb
