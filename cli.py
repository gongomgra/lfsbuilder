"""
cli.py

Command line interface definitions using 'argparse' Python core library.
"""
import argparse

import actions


class Cli(object):
    """
    Cli class.

    Defines parser attributes and usage logic.
    """

    def __init__(self):
        self.basic_parser = None
        self.build_parser = None
        self.download_parser = None
        self.xml_parser = None

    def configure_basic_parser(self):
        """
        Parser options for the 'lfsbuilder.py' main script.
        """
        self.basic_parser = argparse.ArgumentParser()
#            description = "LFSBuilder")
#             usage = """lfsbuilder.py [<options>] <command> [<args>]
# Options:


# Commands:
#   build     Build specified builders
#   parse     Generate XML commands file for specified builder
#   download  Download
# """)

        # Arguments definition
        # .- verbose
        self.basic_parser.add_argument("-v", "--verbose",
                                       help="Output verbose messages",
                                       action="store_true")

        # .- base directory
        self.basic_parser.add_argument("--base-directory",
                                       help="Set base directory",
                                       action=actions.SetConfigOption)

        # .- non privileged username
        self.basic_parser.add_argument("--non-privileged-username",
                                       help="Set non privileged username",
                                       action=actions.SetConfigOption)

        # .- sources orig directory
        self.basic_parser.add_argument("--sources-orig-directory",
                                       help="Set origin directory for sources",
                                       action=actions.SetConfigOption)

        # .- makeflags
        self.basic_parser.add_argument("--makeflags",
                                       help="Set MAKEFLAGS value",
                                       action=actions.SetConfigOption)

        # .- restore XML backups file
        self.basic_parser.add_argument("--restore-xml-backups",
                                       help="Restore XML backups files",
                                       action=actions.SetConfigOption)

        # .- timezone
        self.basic_parser.add_argument("--lfs-version",
                                       help="Version of the book",
                                       action=actions.SetConfigOption)

        # .- command. Save all the arguments starting from the command name until
        # the end of the 'argv' values into a list
        self.basic_parser.add_argument("command",
                                       help="Subcommand to run",
                                       nargs=argparse.REMAINDER)

        # Return configured parser
        return self.basic_parser

    def configure_build_parser(self):
        """
        Parser options for the 'build' command.
        """

        self.build_parser = argparse.ArgumentParser(description="Build specified builders")

        # Arguments definition
        # .- generate-img-file
        group_gen_img_file = self.build_parser.add_mutually_exclusive_group()
        group_gen_img_file.add_argument("--generate-img-file",
                                        action="store_true")

        group_gen_img_file.add_argument("--no-generate-img-file",
                                        action="store_true")

        # .- no mount sources
        group_mount_sources = self.build_parser.add_mutually_exclusive_group()
        group_mount_sources.add_argument("--mount-sources",
                                         action="store_true")

        group_mount_sources.add_argument("--no-mount-sources",
                                         action="store_true")

        # .- mount-img-file
        group_mount_img_file = self.build_parser.add_mutually_exclusive_group()
        group_mount_img_file.add_argument("--mount-img-file",
                                          action="store_true")

        group_mount_img_file.add_argument("--no-mount-img-file",
                                          action="store_true")

        # .- builders list
        self.build_parser.add_argument("builders_list",
                                       action=actions.ModifyBuildersList,
                                       nargs=argparse.REMAINDER)

        # .- mount-system-directories
        group_mount_system_dir = self.build_parser.add_mutually_exclusive_group()
        group_mount_system_dir.add_argument("--mount-system-directories",
                                            action="store_true")

        group_mount_system_dir.add_argument("--no-mount-system-directories",
                                            action="store_true")

        # .- generate data files
        group_data_files = self.build_parser.add_mutually_exclusive_group()
        group_data_files.add_argument("--generate-data-files",
                                      action="store_true")

        group_data_files.add_argument("--no-generate-data-files",
                                      action="store_true")

        # .- boot_manager
        group_boot_manager = self.build_parser.add_mutually_exclusive_group()
        group_boot_manager.add_argument("--sysv",
                                        action="store_true")

        group_boot_manager.add_argument("--systemd",
                                        action="store_true")

        # .- meson builder
        group_meson_builder = self.build_parser.add_mutually_exclusive_group()
        group_meson_builder.add_argument("--include-meson-builder",
                                         action="store_true")

        group_meson_builder.add_argument("--no-include-meson-builder",
                                         action="store_true")

        # .- continue-at
        self.build_parser.add_argument("--continue-at",
                                       action=actions.SetConfigOption)

        # Return configured parser
        return self.build_parser

    def configure_download_parser(self):
        """
        Parser options for the 'download' command.
        """
        # Parse command line arguments
        self.download_parser = argparse.ArgumentParser(description="Download XML and sources")

        # Arguments
        self.download_parser.add_argument("--sources",
                                          action="store_true")
        self.download_parser.add_argument("--xml",
                                          action="store_true")
        self.download_parser.add_argument("--lfs-version",
                                          action=actions.SetConfigOption)

        self.download_parser.add_argument("book_name")

        # Return configured parser
        return self.download_parser

    def configure_xml_parser(self):
        """
        Parser options form the 'parse' command.
        """
        # 'build_parser' already has the required config
        self.xml_parser = self.configure_build_parser()

        # Return configured parser
        return self.xml_parser
