
import os
import sys

import tools
import config
import printer
import components
import xmlparser

class BuilderGenerator(object):

    def __init__(self, builder_name):
        # Read the builder recipe and return a reference to the object type
        self.json_builder_file = "{b}.json".format(b=builder_name)
        self.builder_recipe = os.path.realpath(os.path.join("recipes", "builders",
                                                            builder_name, self.json_builder_file))
        self.attributes_list = ["sources", "tools"]

        # Default values
        self.builder_data_dict = {"name": builder_name,
                                  "env_PATH_value": "${UNSET_VARIABLE}",
                                  "chapters_list": [],
                                  "excludes": [],
                                  "setenv_directory": config.BASE_DIRECTORY,
                                  "book": "lfs"}

        for attribute in self.attributes_list:
            key = "{a}_directory".format(a=attribute)
            value = os.path.join(config.BASE_DIRECTORY, attribute)
            tools.add_to_dictionary(self.builder_data_dict, key, value, concat=False)


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

        # Read recipe
        self.builder_recipe_data = tools.read_recipe_file(self.builder_recipe)
        self.builder_data_dict = tools.join_dicts(self.builder_data_dict, self.builder_recipe_data)

        self.module = "builders"

        # Instanciate a ComponentsBuilder by default
        self.class_fullname = "{m}.ComponentsBuilder".format(m=self.module)

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

    def do_nothing(self):
        pass

    def set_attributes(self):
        if hasattr(self.extra_functions, "set_attributes"):
            # It is not necessary to do nothing in this method right now,
            # but we send 'do_nothing()' as the parent_function to maintain
            # code structure
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


    def generate_commands_file(self):
        if self.builder_data_dict["book"] == "lfs" or \
           self.builder_data_dict["book"] == "blfs":
            # We have to parse book xmlfiles
            xmlp = xmlparser.LFSXmlParser(self.builder_data_dict)
            xmlp.generate_commands_xmlfile()
            del xmlp
        else:
            pass

    def generate_xml_component_data_dict(self):
        self.xml_components_data_dict = {}
        if self.builder_data_dict["book"] == "lfs" or \
           self.builder_data_dict["book"] == "blfs":

            lfsxml = xmlparser.LFSXmlParser()
            self.xml_components_data_dict = lfsxml.generate_dict_from_xmlfile(
                self.builder_data_dict["xml_commands_filename"])
            del lfsxml

        else:
            pass

    def build(self):

        # Create setenv.sh file
        self.create_setenv_script()

        # Generate components_data_dict from XML file
        self.generate_xml_component_data_dict()

        # Build componentsList
        for component in self.builder_data_dict["components_to_build"]:
            printer.info("[*] Building component '{c}'".format(c=component))

            os.chdir(self.builder_data_dict["lfsbuilder_src_directory"])

            # Get component to build reference
            cg = components.ComponentGenerator(component,
                                               self.builder_data_dict,
                                               self.xml_components_data_dict)
            o = cg.get_component_reference()

            # Remove reference to the 'GeneratorComponent'. It is useless
            del cg

            # Build the real component
            o.set_attributes()

            os.chdir(self.builder_data_dict["sources_directory"])
            o.build()

            o.clean_workspace()
            del o

    def clean_workspace(self):
        pass

class ComponentsBuilder(BaseComponentsBuilder):

    def __init__(self, builder_data_dict):
        BaseComponentsBuilder.__init__(self, builder_data_dict)

    def call_build_parent_function(self):
        BaseComponentsBuilder.build(self)

    def build(self):
        if hasattr(self.extra_functions, "build"):
            self.extra_functions.build(self.builder_data_dict,
                                       self.call_build_parent_function)
        else:
            # Call parent function directly
            self.call_build_parent_function()

    def clean_workspace(self):
        BaseComponentsBuilder.clean_workspace(self)
        # Remove 'setenv.sh' file
        os.remove(os.path.join(self.builder_data_dict["setenv_directory"], "setenv.sh"))
