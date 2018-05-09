#!/usr/bin/python

import os
import sys
import argparse

import builders
import config
import tools
import printer
import cli
import actions
import downloader

class LFSBuilder(object):

    def __init__ (self):
        self.lfsbuilder_src_directory = os.path.dirname(os.path.realpath(__file__))
        self.temporal_folder = os.path.join(self.lfsbuilder_src_directory, "tmp")
        self.basic_parser = None
        self.build_parser = None
        self.download_parser = None
        self.xml_parser = None
        self.cli = cli.Cli()

        # Parse sys.args and use dispatcher pattern to
        # invoke method named as command
        self.basic_parser = self.cli.configure_basic_parser()
        self.all_args = self.basic_parser.parse_args()

        # Set boolean configuration flags
        self.set_config_option(self.all_args)

        if not hasattr(self, self.all_args.command[0]):
            printer.warning("Unknown command '{c}'".format(c=self.all_args.command[0]))
            self.basic_parser.print_help()
            sys.exit(1)

        # .- Create 'tmp' directory
        tools.create_directory(self.temporal_folder)

        # Run command
        getattr(self, self.all_args.command[0])()

    def build(self):
        # Parse command line arguments
        self.build_parser = self.cli.configure_build_parser()
        self.build_args = self.build_parser.parse_args(self.all_args.command[1:])

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

        # .- Set 'generate-data-files'
        if "no_generate_data_files" in flags and flags.no_generate_data_files is True:
            setattr(config, "GENERATE_DATA_FILES", False)

        if "generate_data_files" in flags and flags.generate_data_files is True:
            setattr(config, "GENERATE_DATA_FILES", True)

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
        # Parse arguments
        self.download_parser = self.cli.configure_download_parser()
        self.download_args = self.download_parser.parse_args(self.all_args.command[1:])

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

    def parse(self):
        # Parse command line arguments
        self.xml_parser = self.cli.configure_xml_parser()
        self.xml_args = self.xml_parser.parse_args(self.all_args.command[1:])

        # Set GENERATE_DATA_FILES to True to ensure they get created
        setattr(config, "GENERATE_DATA_FILES", True)

        # Generate command file for 'builders_list'
        for builder in self.xml_args.builders_list:
            os.chdir(self.lfsbuilder_src_directory)
            # Generate builder object from BuilderGenerator
            bg = builders.BuilderGenerator(builder)
            o = bg.get_builder_reference()
            del bg
            del o

if __name__ == '__main__':
    lfsb = LFSBuilder()
    del lfsb
