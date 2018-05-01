
import os
import sys

import tools
import config
import printer
import components
import xmlparser

class BuilderGenerator(object):

    def __init__(self, builder_name):

        # Default values
        self.builder_data_dict = {"name": builder_name,
                                  "env_PATH_value": "${UNSET_VARIABLE}",
                                  "chapters_list": [],
                                  "excludes": [],
                                  "components_to_build": [],
                                  "setenv_directory": config.BASE_DIRECTORY,
                                  "book": "lfs"}

        self.attributes_list = ["sources", "tools"]
        for attribute in self.attributes_list:
            key = "{a}_directory".format(a=attribute)
            value = os.path.join(config.BASE_DIRECTORY, attribute)
            tools.add_to_dictionary(self.builder_data_dict, key, value, concat=False)


        # Read the builder recipe and return a reference to the object type
        self.builder_recipe_data = tools.read_recipe_file(self.builder_data_dict["name"],
                                                          directory = "builders")

        # Add 'lfsbuilder_src_directory' to 'self.builder_data_dict'
        tools.add_to_dictionary(self.builder_data_dict, "lfsbuilder_src_directory",
                                os.path.dirname(os.path.realpath(__file__)), concat=False)

        # Add 'lfsbuilder_tmp_directory' to 'self.builder_data_dict'
        tools.add_to_dictionary(self.builder_data_dict, "lfsbuilder_tmp_directory",
                                os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                             "tmp"), concat=False)


        # Add 'xml_commands_filename' to 'self.builder_data_dict' from 'config.py' file. default=None
        tools.add_to_dictionary(self.builder_data_dict, "xml_commands_filename",
                                getattr(config,
                                        "{b}_xml_filename".format(b=self.builder_data_dict["name"]),
                                        None),
                                concat=False)


        # Join dicts. 'self.builder_recipe_data' values will have preference over those
        # currently in 'self.builder_data_dict'
        self.builder_data_dict = tools.join_dicts(self.builder_data_dict,
                                                  self.builder_recipe_data)

        # Module name
        self.module = "builders"

        # Instantiate a ComponentsBuilder by default
        self.class_fullname = "{m}.ComponentsBuilder".format(m=self.module)

        # Instantiate a 'InfrastructureComponentsBuilder' if required
        if "base_builder" in self.builder_data_dict and \
           self.builder_data_dict["base_builder"].lower() == "infrastructurecomponentsbuilder":
            self.class_fullname = "{m}.{t}".format(m = self.module,
                                                   t = "InfrastructureComponentsBuilder")

        # Create object
        self.obj = tools.get_class(self.class_fullname)

    def get_builder_reference(self):
        return self.obj(self.builder_data_dict)


class BaseBuilder(object):

    def __init__(self, builder_data_dict):
        self.builder_data_dict = tools.join_dicts({}, builder_data_dict)

        # Get 'functions.py' if any
        self.extra_functions = tools.read_functions_file(self.builder_data_dict["name"],
                                                         directory="builders")

        # Get 'components_to_build_list' if necessary
        if hasattr(self.extra_functions, "get_components_to_build_list"):
            self.extra_functions.get_components_to_build_list(self.builder_data_dict,
                                                              self.get_components_to_build_list)
        else:
            self.get_components_to_build_list()

    def get_components_to_build_list(self):
        # Get 'components_to_build' list from book if necessary
        if config.CUSTOM_COMPONENTS_TO_BUILD is False and \
           (self.builder_data_dict["name"] == "toolchain" or \
            self.builder_data_dict["name"] == "system" or \
            self.builder_data_dict["name"] == "configuration" or \
            self.builder_data_dict["name"] == "blfs"):

            self.index_filename = "{n}_components_to_build.txt".format(n=self.builder_data_dict["name"])
            self.index_filename_path = os.path.join(self.builder_data_dict["lfsbuilder_tmp_directory"],
                                                    self.index_filename)
            tools.add_to_dictionary(self.builder_data_dict,
                                    "components_to_build",
                                    tools.list_from_file(self.index_filename_path),
                                    concat=False)
        else:
            pass

    def do_nothing(self):
        pass

    def set_attributes(self):
        if hasattr(self.extra_functions, "set_attributes"):
            self.extra_functions.set_attributes(self.builder_data_dict,
                                                self.do_nothing)

    def build(self):
        pass

    def create_setenv_script(self):
        filename = os.path.join(self.builder_data_dict["setenv_directory"], "setenv.sh")

        text = """# Builder: '@@LFS_BUILDER_NAME@@'

# Do not locate and remember (hash) commands as they are looked up for execution
set +h

# Any command which fail will cause the shell script to exit immediately
set -e

# Any command will fail if using any unset variable. For example: "sudo rm -rf /${UNSET_VARIABLE}*"
# won't run "sudo rm /*". It will fail instead
set -u

# Default umask value
umask 022

# LFS custom PATH
PATH=@@LFS_ENV_PATH_VALUE@@
export PATH

# LFS mount point
LFS=@@LFS_BASE_DIRECTORY@@
export LFS

# LFS target kernel name
LFS_TGT=$(uname -m)-lfs-linux-gnu
export LFS_TGT

LC_ALL=POSIX
export LC_ALL

# LFS compile core numbers
MAKEFLAGS='@@LFS_MAKEFLAGS@@'
export MAKEFLAGS

# Terminal has full of colors
TERM=xterm-256color
export TERM
"""
        # Write file
        tools.write_file(filename, text)

        # Substitute parameters
        substitution_list = ["@@LFS_BUILDER_NAME@@", self.builder_data_dict["name"],
                             "@@LFS_ENV_PATH_VALUE@@", self.builder_data_dict["env_PATH_value"],
                             "@@LFS_SOURCES_DIRECTORY@@", self.builder_data_dict["sources_directory"],
                             "@@LFS_TOOLS_DIRECTROY@@", self.builder_data_dict["tools_directory"],
                             "@@LFSBUILDER_SRC_DIRECTORY@@", self.builder_data_dict["lfsbuilder_src_directory"],
                             "@@LFS_BASE_DIRECTORY@@", config.BASE_DIRECTORY,
                             "@@LFS_MAKEFLAGS@@", config.MAKEFLAGS]

        tools.substitute_multiple_in_file(filename, substitution_list)

class BaseComponentsBuilder(BaseBuilder):

    def __init__(self, builder_data_dict):
        BaseBuilder.__init__(self, builder_data_dict)

        self.component_data_dict = {}

    def generate_data_files(self):
        if self.builder_data_dict["book"] == "lfs" or \
           self.builder_data_dict["book"] == "blfs":
            # We have to parse book xmlfiles
            xmlp = xmlparser.LFSXmlParser(self.builder_data_dict)
            xmlp.generate_commands_xmlfile()
            del xmlp
        else:
            pass

    def generate_xml_components_data_dict(self):
        self.xml_components_data_dict = {}
        if self.builder_data_dict["book"] == "lfs" or \
           self.builder_data_dict["book"] == "blfs":

            lfsxml = xmlparser.LFSXmlParser(self.builder_data_dict)
            self.xml_components_data_dict = lfsxml.generate_dict_from_xmlfile(
                self.builder_data_dict["xml_commands_filename"])
            del lfsxml

        else:
            pass

    def build_components(self):

        # Create setenv.sh file
        self.create_setenv_script()

        # Generate components_data_dict from XML file
        self.generate_xml_components_data_dict()

        # Build componentsList
        for component in self.builder_data_dict["components_to_build"]:
            printer.info("[*] Building component '{c}'".format(c=component))

            os.chdir(self.builder_data_dict["lfsbuilder_src_directory"])

            # Get component to build reference
            cg = components.ComponentGenerator(component,
                                               self.builder_data_dict,
                                               self.xml_components_data_dict)
            o = cg.get_component_reference()

            # Remove reference to the 'ComponentGenerator'. It is useless
            del cg

            # Build the real component
            o.set_attributes()

            os.chdir(self.builder_data_dict["sources_directory"])
            o.build()

            o.clean_workspace()
            del o

    def build(self):
        if hasattr(self.extra_functions, "build"):
            self.extra_functions.build(self.builder_data_dict,
                                       self.build_components)
        else:
            # Call parent function directly
            self.build_components()

    def clean_workspace(self):
        # Remove 'setenv.sh' file
        os.remove(os.path.join(self.builder_data_dict["setenv_directory"], "setenv.sh"))

class InfrastructureComponentsBuilder(BaseComponentsBuilder):

    def __init__(self, builder_data_dict):
        BaseComponentsBuilder.__init__(self, builder_data_dict)

        # Build components from the 'lfs_src_directory/tmp' directory
        tools.add_to_dictionary(self.builder_data_dict,
                                "setenv_directory",
                                builder_data_dict["lfsbuilder_tmp_directory"],
                                concat=False)

        tools.add_to_dictionary(self.builder_data_dict,
                                "sources_directory",
                                builder_data_dict["lfsbuilder_tmp_directory"],
                                concat=False)

class ComponentsBuilder(BaseComponentsBuilder):

    def __init__(self, builder_data_dict):
        BaseComponentsBuilder.__init__(self, builder_data_dict)
