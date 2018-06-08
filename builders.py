"""
builders.py

Builders definitions.
"""
import os

import tools
import config
import printer
import components
import xmlparser


class BuilderGenerator(object):
    """
    BuilderGenerator class.

    It generates the required Builder class type depending on
    values obtained from the recipe file.
    """
    def __init__(self, builder_name):

        # Default values
        self.builder_data_dict = {
            "name": builder_name,
            "env_PATH_value": "${UNSET_VARIABLE}",
            "chapters_list": [],
            "excludes": [],
            "components_to_build": [],
            "setenv_directory": config.BASE_DIRECTORY,
            "setenv_filename": "setenv.sh",
            "setenv_template": "setenv.tpl",
            "book": "lfs",
            "runscript_cmd": "env -i /bin/bash",
            "base_module": "builders",
            "base_builder": "ComponentsBuilder",
            "sources_directory": os.path.join(config.BASE_DIRECTORY,
                                              "sources"),
            "tools_directory": os.path.join(config.BASE_DIRECTORY, "tools"),
            "lfsbuilder_src_directory": os.path.dirname(
                os.path.realpath(__file__)
            ),
            "lfsbuilder_tmp_directory": os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "tmp"),
            "lfsbuilder_templates_directory": os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "templates")
        }

        # Read the builder recipe and return a reference to the object type
        self.builder_recipe_data = tools.read_recipe_file(
            self.builder_data_dict["name"],
            directory="builders")

        # Add 'xml_commands_filename' to 'self.builder_data_dict'
        # from 'config.py' file. default=None
        getattr_data_value = self.builder_data_dict["name"].upper()
        tools.add_to_dictionary(self.builder_data_dict,
                                "xml_commands_filename",
                                getattr(config,
                                        "{b}_XML_FILENAME".format(
                                            b=getattr_data_value),
                                        None),
                                concat=False)

        # Join dicts. 'self.builder_recipe_data' values will have preference
        # over those currently in 'self.builder_data_dict' (defaults)
        self.builder_data_dict = tools.join_dicts(self.builder_data_dict,
                                                  self.builder_recipe_data)

        # Include '-x' parameter to the 'runscript_cmd'
        # if 'config.DEBUG_SCRIPTS' is 'True'
        if config.DEBUG_SCRIPTS is True:
            value = "{c} -x".format(c=self.builder_data_dict["runscript_cmd"])
            tools.add_to_dictionary(
                self.builder_data_dict,
                "runscript_cmd",
                value,
                concat=False
            )

        # Instantiate a ComponentsBuilder by default
        self.class_fullname = "{m}.{t}".format(
            m=self.builder_data_dict["base_module"],
            t=self.builder_data_dict["base_builder"]
        )

        # Instantiate a 'InfrastructureComponentsBuilder' if required
        if self.builder_data_dict["base_builder"].lower() == "componentsbuilder":
            self.class_fullname = "{m}.{t}".format(
                m=self.builder_data_dict["base_module"],
                t="ComponentsBuilder"
            )

        elif self.builder_data_dict["base_builder"].lower() == "infrastructurecomponentsbuilder":
            self.class_fullname = "{m}.{t}".format(
                m=self.builder_data_dict["base_module"],
                t="InfrastructureComponentsBuilder"
            )

        else:
            text = "Unknown 'base_builder': '{b}'"
            text = text.format(b=self.builder_data_dict["base_builder"])
            printer.error(text)

        # Create object
        self.obj = tools.get_class(self.class_fullname)

    def get_builder_reference(self):
        """
        Return memory reference for the generate builder object.
        """
        return self.obj(self.builder_data_dict)


class BaseBuilder(object):
    """
    BaseBuilder class.
    """
    def __init__(self, builder_data_dict):
        self.builder_data_dict = tools.join_dicts({}, builder_data_dict)

        # Current books names and available builders.
        self.book_names = ["lfs", "blfs"]
        self.book_builders = ["toolchain", "system", "configuration"]

        # Get 'functions.py' if any
        self.extra_functions = tools.read_functions_file(self.builder_data_dict["name"],
                                                         directory="builders")

        # Generate data files if necessary
        if config.GENERATE_DATA_FILES is True:
            self.generate_data_files()

        # Get 'components_to_build_list' if necessary
        if hasattr(self.extra_functions, "get_components_to_build_list"):
            self.extra_functions.get_components_to_build_list(self.builder_data_dict,
                                                              self.get_components_to_build_list)
        else:
            self.get_components_to_build_list()

    def generate_data_files(self):
        """
        Generate 'builder_data.xml' and 'builder_components_to_file.txt' files.
        """
        if self.builder_data_dict["book"] in self.book_names:
            # We have to parse book xmlfiles
            xmlp = xmlparser.LFSXmlParser(self.builder_data_dict)
            xmlp.generate_commands_xmlfile()
            del xmlp
        else:
            pass

    def get_components_to_build_list(self):
        """
        Get 'components_to_build' list from book if necessary.
        """
        if config.CUSTOM_COMPONENTS_TO_BUILD is False and \
           self.builder_data_dict["name"] in self.book_builders:

            # Get 'components_to_build' from book
            self.index_filename = "{n}_components_to_build.txt"
            self.index_filename = self.index_filename.format(n=self.builder_data_dict["name"])
            self.index_filename_path = os.path.join(
                self.builder_data_dict["lfsbuilder_tmp_directory"],
                self.index_filename
            )
            # Update dictionary entry
            tools.add_to_dictionary(self.builder_data_dict,
                                    "components_to_build",
                                    tools.list_from_file(self.index_filename_path),
                                    concat=False)

        # .- continue-at
        if config.CONTINUE_AT is not None and \
           self.builder_data_dict["name"] in self.book_builders:
            # .- Try to start from the 'continue-at' component
            self.continue_at()

    def continue_at(self):
        """
        Start from the 'config.CONTINUE_AT' component of the first provided builder.
        Fails in case this component do not exist.
        """
        # .- is component present
        if tools.is_element_present(self.builder_data_dict["components_to_build"],
                                    config.CONTINUE_AT) is True:
            # get component index and trim 'components_to_build' list
            index = tools.get_element_index(self.builder_data_dict["components_to_build"],
                                            config.CONTINUE_AT)
            # trim list and update 'self.builder_data_dict' value
            aux_list = self.builder_data_dict["components_to_build"][index:]
            tools.add_to_dictionary(self.builder_data_dict,
                                    "components_to_build",
                                    aux_list,
                                    concat=False)
            # .- set 'config.CONTINUE_AT' to 'None' so we do not get into this method
            # any more on the current execution
            setattr(config, "CONTINUE_AT", None)
        else:
            text = """'continue-at' component '{c}' do not exists on the \
'components_to_build' list for the '{b}' builder""".format(c=config.CONTINUE_AT,
                                                           b=self.builder_data_dict["name"])
            printer.error(text)

    def do_nothing(self):
        """
        Dummy function to maintain code structure. Does nothing.
        """
        pass

    def set_attributes(self):
        """
        Set attributes after running the '__init__' method. Can be overwritted in the
        'functions.py' file of the builder recipe directory to customize builder attributes.
        If so, arguments are:
            - 'builder_data_dict': current builder data, which can be accessed and modified.
            - 'parent_function': parent method reference.
       """
        if hasattr(self.extra_functions, "set_attributes"):
            self.extra_functions.set_attributes(self.builder_data_dict,
                                                self.do_nothing)

    def build(self):
        """
        Steps to build current 'builder'.
        """
        pass

    def create_setenv_script(self):
        """
        Create the 'setenv.sh' file from the 'templates/setenv.tpl' template under the
        lfsbuilder source directory.
        """
        setenv_filename = os.path.join(self.builder_data_dict["setenv_directory"],
                                       self.builder_data_dict["setenv_filename"])

        template = os.path.join(self.builder_data_dict["lfsbuilder_templates_directory"],
                                self.builder_data_dict["setenv_template"])

        substitution_list = ["@@LFS_BUILDER_NAME@@", self.builder_data_dict["name"],
                             "@@LFS_ENV_PATH_VALUE@@", self.builder_data_dict["env_PATH_value"],
                             "@@LFS_SOURCES_DIRECTORY@@",
                             self.builder_data_dict["sources_directory"],
                             "@@LFS_TOOLS_DIRECTROY@@", self.builder_data_dict["tools_directory"],
                             "@@LFSBUILDER_SRC_DIRECTORY@@",
                             self.builder_data_dict["lfsbuilder_src_directory"],
                             "@@LFS_BASE_DIRECTORY@@", config.BASE_DIRECTORY,
                             "@@LFS_MAKEFLAGS@@", config.MAKEFLAGS]

        # Copy template
        tools.copy_file(template, setenv_filename)

        # Substitute parameters
        tools.substitute_multiple_in_file(setenv_filename, substitution_list)


class BaseComponentsBuilder(BaseBuilder):
    """
    BaseComponentsBuilder.
    """

    def __init__(self, builder_data_dict):
        BaseBuilder.__init__(self, builder_data_dict)

        self.xml_components_data_dict = {}
        self.component_data_dict = {}

    def generate_xml_components_data_dict(self):
        """
        Generates data files (commands, and components_to_build) for the current builder.
        """
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
        """
        Stepts to build components of the 'components_to_build' list attribute.
        """
        # Create setenv.sh file
        self.create_setenv_script()

        # Generate components_data_dict from XML file
        self.generate_xml_components_data_dict()

        # Build componentsList
        i = 1
        for component in self.builder_data_dict["components_to_build"]:
            msg = "[{i}/{n}] Building component '{c}'"
            msg = msg.format(
                i=i,
                n=len(self.builder_data_dict["components_to_build"]),
                c=component
            )
            printer.info(msg)

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

            # Update index
            i += 1

    def build(self):
        """
        Steps to build current 'builder'.
        """
        if hasattr(self.extra_functions, "build"):
            self.extra_functions.build(self.builder_data_dict,
                                       self.build_components)
        else:
            # Call parent function directly
            self.build_components()

    def clean_workspace(self):
        """
        Clean used workspace to build current builder.
        """
        # Remove 'setenv.sh' file
        filepath = (
            os.path.join(
                self.builder_data_dict["setenv_directory"],
                self.builder_data_dict["setenv_filename"]
            )
        )

        if os.path.exists(filepath):
            os.remove(filepath)


class InfrastructureComponentsBuilder(BaseComponentsBuilder):
    """
    InfrastructureComponentsBuilder class.

    Build components that configure the building environment for the rest of the components,
    e.g. create the image file, mount the 'sources' directories...
    """
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
    """
    ComponentsBuilder class.

    Build components into the final system according to the values of both the 'component' recipe
    and book commands if necessary.
    """
    def __init__(self, builder_data_dict):
        BaseComponentsBuilder.__init__(self, builder_data_dict)
