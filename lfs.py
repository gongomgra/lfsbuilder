# LFS class
import os
import sys

import builders
import config
import tools

class LFS(object):

    def __init__ (self, arguments):
        # tools.pretty_print(arguments)
        # print "len: '{l}'".format(l=len(arguments))
        self.action = arguments[1]
        self.build_list = []
        self.temporal_folder = "tmp"
        self.lfsbuilder_src_directory = os.path.dirname(os.path.realpath(__file__))

    def execute(self):
        actions = {
            "help": self.usage,
            "build": self.build,
        }

        # Execute provided order
        if self.action == "build":
            actions[self.action](sys.argv[2:])
        else:
            actions[self.action]()

    def build(self, build_list):
        # Create 'tmp' directory
        tools.create_directory(self.temporal_folder)
        # Create required builder and call its build method

        print "build_list: {b}".format(b=build_list)

        # If we are going to build
        if build_list[-1] is "configuration":
            setattr(sys.modules["config"], "IS_CONFIGURATION_LAST", True)
        else:
            setattr(sys.modules["config"], "IS_CONFIGURATION_LAST", False)

        for builder in build_list:
            os.chdir(self.lfsbuilder_src_directory)
            # Generate builder object from BuilderGenerator
            bg = builders.BuilderGenerator(builder)
            o = bg.get_builder_reference()
            del bg

            # Run the real builder
            o.set_attributes()

            if o.builder_data_dict["book"] == "lfs" or \
               o.builder_data_dict["book"] == "blfs":
                o.generate_commands_file()

            o.build()
            del o
            print "---"

    def usage(self):
        print """
 _     _____ ____  ____        _ _     _
| |   |  ___/ ___|| __ ) _   _(_) | __| | ___ _ __
| |   | |_  \___ \|  _ \| | | | | |/ _` |/ _ \ '__|
| |___|  _|  ___) | |_) | |_| | | | (_| |  __/ |
|_____|_|   |____/|____/ \__,_|_|_|\__,_|\___|_|

Usage:

 lfsbuilder [options] [command] [arguments]

Options:
 -v, --verbose          verbose mode

Command:
 help                   show this help
 build <builders list>  run builders specified
       all              run all the builders

"""




        # if self.action == "toolchain":
        #     t = builders.ToolchainBuilder()
        #     # Generate 'toolchain' commands XML file
        #     t.generate_commands_file()
        #     # Build 'toolchain' using commands in XML file
        #     t.build()
        #     # Delete object
        #     del t

        # if self.action == "system":
        #     s = builders.SystemBuilder()
        #     # Generate 'system' commands XML file
        #     s.generate_commands_file()
        #     # Build 'system' using commands in XML file
        #     s.build()
        #     # Delete object
        #     del s

        # if self.action == "configuration":
        #     c = builders.ConfigurationBuilder()
        #     # Generate 'configuration' commands XML file
        #     c.generate_commands_file()
        #     # Build 'configuration' using commands in XML file
        #     c.build()
        #     # Delete object
        #     del c
