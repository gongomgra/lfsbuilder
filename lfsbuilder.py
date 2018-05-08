#!/usr/bin/python

import os
import sys
import argparse

import builders
import config
import tools
import printer
import actions
import downloader

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
                                 action=actions.SetConfigOption)

        # .- non privileged username
        self.parser.add_argument("--non-privileged-username",
                                 help="Set non privileged username",
                                 action=actions.SetConfigOption)

        # .- sources orig directory
        self.parser.add_argument("--sources-orig-directory",
                                 help="Set origin directory for sources",
                                 action=actions.SetConfigOption)

        # .- makeflags
        self.parser.add_argument("--makeflags",
                                 help="Set MAKEFLAGS value",
                                 action=actions.SetConfigOption)

        # .- restore XML backups file
        self.parser.add_argument("--restore-xml-backups",
                                 help="Restore XML backups files",
                                 action=actions.SetConfigOption)

        # .- timezone
        self.parser.add_argument("--lfs-version",
                                 help="Version of the book",
                                 action=actions.SetConfigOption)

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

        # .- Create 'tmp' directory
        tools.create_directory(self.temporal_folder)

        # Run command
        getattr(self, self.all_args.command[0])()

    def build(self):
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description = "Build specified builders",
            usage = "Usage for build")

        # Arguments definition
        # .- generate-img-file
        group_gen_img_file = parser.add_mutually_exclusive_group()
        group_gen_img_file.add_argument("--generate-img-file",
                                        action = "store_true")

        group_gen_img_file.add_argument("--no-generate-img-file",
                                        action = "store_true")

        # .- no mount sources
        group_mount_sources = parser.add_mutually_exclusive_group()
        group_mount_sources.add_argument("--mount-sources",
                                         action = "store_true")

        group_mount_sources.add_argument("--no-mount-sources",
                                         action = "store_true")

        # .- mount-img-file
        group_mount_img_file = parser.add_mutually_exclusive_group()
        group_mount_img_file.add_argument("--mount-img-file",
                                          action = "store_true")

        group_mount_img_file.add_argument("--no-mount-img-file",
                                          action = "store_true")

        # .- builders list
        parser.add_argument("builders_list",
                            action=actions.ModifyBuildersList,
                            nargs=argparse.REMAINDER)

        # .- mount-system-directories
        group_mount_system_dir = parser.add_mutually_exclusive_group()
        group_mount_system_dir.add_argument("--mount-system-directories",
                                            action = "store_true")

        group_mount_system_dir.add_argument("--no-mount-system-directories",
                                            action = "store_true")

        # .- boot_manager
        group_boot_manager = parser.add_mutually_exclusive_group()
        group_boot_manager.add_argument("--sysv",
                                        action = "store_true")

        group_boot_manager.add_argument("--systemd",
                                        action = "store_true")

        # .- meson builder
        group_meson_builder = parser.add_mutually_exclusive_group()
        group_meson_builder.add_argument("--include-meson-builder",
                                         action = "store_true")

        group_meson_builder.add_argument("--no-include-meson-builder",
                                         action = "store_true")


        # Parse arguments
        self.build_args = parser.parse_args(self.all_args.command[1:])

        # Set boolean configuration flags
        self.set_config_option(self.build_args)

        # .- Check boot manager and meson builder combination
        if tools.is_element_present(self.build_args.builders_list, "system") is True and \
           self.check_meson_builder_combination(m = config.INCLUDE_MESON_BUILDER,
                                                sv = config.SYSV,
                                                sd = config.SYSTEMD) is False:
            printer.error("You can not use that combination of 'boot_manager' and 'meson builder'")

        # Create and build 'builders_list'
        for builder in self.build_args.builders_list:
            os.chdir(self.lfsbuilder_src_directory)
            # Generate builder object from BuilderGenerator
            bg = builders.BuilderGenerator(builder)
            o = bg.get_builder_reference()
            del bg

            # Generate data files if necessary
            o.generate_data_files()

            # Run the real builder
            o.set_attributes()

            o.build()
            o.clean_workspace()
            del o


    def set_config_option(self, flags):

        # .- Set 'verbose'
        if "verbose" in flags and flags.verbose is True:
            setattr(config, "VERBOSE", True)

        # .- Set 'generate_img_file'
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
            setattr(config, "MOUNT_SYSTEM_BUILDER_DIRECTORIES", False)

        if "mount_system_directories" in flags and flags.mount_system_directories is True:
            setattr(config, "MOUNT_SYSTEM_BUILDER_DIRECTORIES", True)

        # .- Set 'sysv' and 'systemd'
        if "sysv" in flags and flags.sysv is True:
            setattr(config, "SYSV", True)
            setattr(config, "SYSTEMD", False)
            setattr(config, "EXCLUDED_BOOT_MANAGER", "systemd")

        elif "systemd" in flags and flags.systemd is True:
            setattr(config, "SYSTEMD", True)
            setattr(config, "SYSV", False)
            setattr(config, "EXCLUDED_BOOT_MANAGER", "sysv")

        else:
            # Sanitize input from 'config.py'
            setattr(config, "SYSV", bool(config.SYSV))
            setattr(config, "SYSTEMD", bool(config.SYSTEMD))
            # Supose we are building 'sysv' by default
            setattr(config, "EXCLUDED_BOOT_MANAGER", "systemd")
            if config.SYSTEMD is True:
                setattr(config, "EXCLUDED_BOOT_MANAGER", "sysv")

        # .- Set 'include meson builder'
        if "include_meson_builder" in flags and flags.include_meson_builder is True:
            setattr(config, "INCLUDE_MESON_BUILDER", True)
        elif "no_include_meson_builder" in flags and flags.no_include_meson_builder is True:
            setattr(config, "INCLUDE_MESON_BUILDER", False)
        else:
            # Sanitize input from 'config.py'
            setattr(config, "INCLUDE_MESON_BUILDER", bool(config.INCLUDE_MESON_BUILDER))


    def check_meson_builder_combination(self, m, sv, sd):
        """
        This function checks if provided 'boot manager' and 'meson builder' selected or not combination
is valid by implementing solution for the below Karnaugh map

  \ sv,sd
m  \   00   01   11   10
    +____________________+
0   |  0  | 0  | 0  | 1  |
    +-----+----+----+----+
1   |  0  | 1  | 0  | 1  |
    +-----+----+----+----+

"""
        return (m and not(sv) and sd) or (sv and not(sd))


    def download(self):
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description = "Download XML and sources")

        # Arguments
        parser.add_argument("--sources",
                            action = "store_true")
        parser.add_argument("--xml",
                            action = "store_true")
        parser.add_argument("book_name")

        # Parse arguments
        self.download_args = parser.parse_args(self.all_args.command[1:])

        # Sanitize book name from input
        self.download_args.book_name = self.download_args.book_name.lower()

        if self.download_args.book_name != "lfs" and self.download_args.book_name != "blfs":
            printer.warning("Unknown book name for download: '{b}'".format(
                b=self.download_args.book_name))
            # self.parser.print_help()
            sys.exit(1)

        # Run downloader
        d = downloader.Downloader(self.download_args.book_name)

        # Run download method
        if self.download_args.sources is True:
            d.download_source()
        elif self.download_args.xml is True:
            d.download_xml()
        else:
            printer.warning("You must provide any of the '--xml' or '--sources' options")
            # self.parser.print_help()
            sys.exit(1)

if __name__ == '__main__':
    lfsb = LFSBuilder()
    del lfsb