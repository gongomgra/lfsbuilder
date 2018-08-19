"""
components.py

Components definitions.
"""
import os
import shutil

import tools
import config
import printer


class ComponentGenerator(object):
    """
    ComponentGenerator class.

    Generates the required Component class type depending on
    values obtained from the recipe file
    """
    def __init__(self, component_name, builder_data_dict, xml_components_data_dict):

        self.component_data_defaults = {
            "name": component_name,
            "show_name": component_name,
            "key_name": component_name,
            "package_name": component_name,
            "version": None,

            "extracted_directory": None,
            "build_directory_path": None,
            "buildscript_path": None,
            "require_build_dir": False,
            "run_as_username": config.NON_PRIVILEGED_USERNAME,
            "runscript_cmd": builder_data_dict["runscript_cmd"],

            "sources_directory":
            "{b}/sources".format(b=config.BASE_DIRECTORY),

            "builder_name": builder_data_dict["name"],
            "component_substitution_list": None,
            "disable_commands_list": None,

            "configure": None,
            "make": None,
            "install": None,
            "test": None,
            "include_tests": None,
            "configure_options": None,
            "make_options": None,
            "install_options": None,
            "test_options": None,

            "base_module": "components",
            "base_component": "CompilableComponent",

            "setenv_directory": builder_data_dict["setenv_directory"],
            "setenv_filename": builder_data_dict["setenv_filename"],

            "build_into_chroot": builder_data_dict["build_into_chroot"],
            "script_template": "script.tpl",

            "lfsbuilder_src_directory": builder_data_dict["lfsbuilder_src_directory"],
            "lfsbuilder_tmp_directory": builder_data_dict["lfsbuilder_tmp_directory"],
            "lfsbuilder_templates_directory": builder_data_dict["lfsbuilder_templates_directory"]
        }

        # Update keys, values that match the 'key_name'
        # from 'xml_components_data_dict'
        for key, value in xml_components_data_dict.items():
            if key.startswith(self.component_data_defaults["key_name"]):
                # Rename 'component named' keys removing the 'component_name' and add to dictionary
                new_key = key.replace("{c}_".format(c=self.component_data_defaults["key_name"]),
                                      "")

                tools.add_to_dictionary(self.component_data_defaults, new_key, value, concat=False)

        # Read component recipe
        self.component_recipe_data = tools.read_recipe_file(component_name)
        self.component_data_dict = tools.join_dicts(self.component_data_defaults,
                                                    self.component_recipe_data)

        # Cast 'require_build_dir' from string to bool
        # bool(int 1) = True
        # bool(int 0) = False
        if "require_build_dir" in self.component_data_dict and \
           self.component_data_dict["require_build_dir"] is not None:
            # Update value
            tools.add_to_dictionary(
                self.component_data_dict,
                "require_build_dir",
                bool(int(self.component_data_dict["require_build_dir"])),
                concat=False
            )

        elif "require_build_dir" in self.component_data_dict and \
             self.component_data_dict["require_build_dir"] is None:
            # Set 'require_build_dir' to 'False'
            tools.add_to_dictionary(
                self.component_data_dict,
                "require_build_dir",
                False,
                concat=False
            )

        else:
            # Set 'require_build_dir' to 'False'
            tools.add_to_dictionary(
                self.component_data_dict,
                "require_build_dir",
                False,
                concat=False
            )

        # Ensure 'run_into_chroot' is a boolean value
        if "build_into_chroot" in self.component_data_dict and \
           self.component_data_dict["build_into_chroot"] is not None:
            # Update value
            tools.add_to_dictionary(
                self.component_data_dict,
                "build_into_chroot",
                bool(int(self.component_data_dict["build_into_chroot"])),
                concat=False
            )

        elif "build_into_chroot" in self.component_data_dict and \
             self.component_data_dict["build_into_chroot"] is None:
            # Set 'build_into_chroot' to 'False'
            tools.add_to_dictionary(
                self.component_data_dict,
                "build_into_chroot",
                False,
                concat=False
            )

        else:
            # Set 'build_into_chroot' to 'False'
            tools.add_to_dictionary(
                self.component_data_dict,
                "build_into_chroot",
                False,
                concat=False
            )

        # Process 'component_substitution_list'
        if self.component_data_dict["component_substitution_list"] is not None:
            tools.process_component_substitution_list(
                self.component_data_dict["component_substitution_list"]
            )

        # Instanciate component object.
        # Select component type for instance
        # .- CompilableComponent
        if self.component_data_dict["base_component"].lower() == "compilablecomponent":
            self.class_fullname = "{m}.{t}".format(m=self.component_data_dict["base_module"],
                                                   t="CompilableComponent")

        # .- SystemConfigurationComponent
        elif self.component_data_dict["base_component"].lower() == "systemconfigurationcomponent":
            self.class_fullname = "{m}.{t}".format(m=self.component_data_dict["base_module"],
                                                   t="SystemConfigurationComponent")

        else:
            text = "Unknown 'base_component': '{b}'"
            text = text.format(b=self.component_data_dict["base_component"])
            printer.error(text)

        # Create object
        self.obj = tools.get_class(self.class_fullname)

    def get_component_reference(self):
        """
        Returns memory reference for the generated component.
        """
        return self.obj(self.component_data_dict)


class BaseComponent(object):
    """
    BaseComponent class.
    """

    def __init__(self, component_data_dict):
        self.tools_directory = os.path.join(config.BASE_DIRECTORY, "tools")
        self.component_data_dict = tools.join_dicts({}, component_data_dict)
        self.attributes_list = ["show_name", "key_name", "package_name"]

        # Read 'functions.py' file
        self.extra_functions = tools.read_functions_file(self.component_data_dict["name"])

    def do_nothing(self):
        """
        Dummy function to maintain code structure. Does nothing.
        """
        pass

    def set_attributes(self):
        """
        Set attributes after running the '__init__' method. Can be overwritten in the
        'function.py' file under the component recipe directory to customize
        component's attributes.
        If so, arguments are:
            - 'component_data_dict': current component data, which can be accessed and modified.
            - 'parent_function': parent method reference.
        """
        if hasattr(self.extra_functions, "set_attributes"):
            # It is not necessary to do nothing in this method right now,
            # but we send 'do_nothing()' as the parent_function to maintain
            # code structure
            self.extra_functions.set_attributes(self.component_data_dict,
                                                self.do_nothing)

    def build(self):
        """
        Steps to build current 'component'.
        """
        pass

    def get_command_to_run_script(self, filename):
        """
        Command to execute on the build directory to run scripts.
        """
        # Remove BASE_DIRECTORY if we are inside the chroot.
        # We are not related to BASE_DIRECTORY anymore
        if self.component_data_dict["build_into_chroot"] is True:
            filename = filename.replace(config.BASE_DIRECTORY, "")

        cmd = "{c} {f}".format(c=self.component_data_dict["runscript_cmd"],
                               f=filename)

        return cmd

    def substitute_script_placeholders(self, file_path=None):
        """
        Substitute common '@@LFS_' placeholders in the provided script by 'file_path'.
        Fails if there is any placeholder pending.
        """
        # Run substitution twice to ensure composed placeholders get susbstitute
        substitution_rounds = 2

        # Substitute in buildscript by default
        if file_path is None:
            file_path = self.component_data_dict["buildscript_path"]

        # Generate setenv file path.
        # Remove BASE_DIRECTORY from path if we are not building the 'toolchain'
        setenv_script_path = os.path.realpath(os.path.join(
            self.component_data_dict["setenv_directory"],
            self.component_data_dict["setenv_filename"]))

        if self.component_data_dict["build_into_chroot"] is True:
            # If we are into the chroot, setenv.sh is located at root directory (/setenv.sh)
            # so we remove that part of the 'setenv_script_path' variable
            setenv_script_path = setenv_script_path.replace(config.BASE_DIRECTORY, "")

        # Placeholders to substitute
        substitution_list = ["@@LFS_SETENV_FILE@@",
                             setenv_script_path,

                             "@@LFS_COMPONENT_KEYNAME@@",
                             self.component_data_dict["key_name"],

                             "@@LFS_BUILDER_NAME@@",
                             self.component_data_dict["builder_name"],

                             "@@LFSBUILDER_SRC_DIRECTORY@@",
                             self.component_data_dict["lfsbuilder_src_directory"],

                             "@@LFSBUILDER_TMP_DIRECTORY@@",
                             self.component_data_dict["lfsbuilder_tmp_directory"],

                             "@@LFS_SOURCES_DIRECTORY@@",
                             self.component_data_dict["sources_directory"],

                             "@@LFS_BASE_DIRECTORY@@",
                             config.BASE_DIRECTORY,

                             "@@LFS_VERSION@@",
                             config.LFS_VERSION,

                             "&amp;",
                             "&",

                             "&gt;",
                             ">",

                             "&lt;",
                             "<",

                             "&quot;",
                             "\""]

        # Add component substitution list
        if self.component_data_dict["component_substitution_list"] is not None:
            substitution_list.extend(
                self.component_data_dict["component_substitution_list"]
            )

        # Remove BASE_DIRECTORY if not building 'toolchain'
        if self.component_data_dict["build_into_chroot"] is True:
            substitution_list.extend([config.BASE_DIRECTORY, ""])

        # Substitute
        i = 0
        while i < substitution_rounds:
            tools.substitute_multiple_in_file(file_path, substitution_list)
            # update loop index
            i += 1

        # Check there are not any pending placeholder
        text = tools.read_file(file_path)
        if text.find("@@LFS") != -1:
            printer.error("Found pending placeholder in '{f}'".format(f=file_path))

    def copy_script_header(self, script_filename):
        """
        Copy script header from the 'script.tpl' template under the 'templates' directory.
        """
        template = os.path.join(self.component_data_dict["lfsbuilder_templates_directory"],
                                self.component_data_dict["script_template"])

        printer.substep_info("Generating script '{f}'".format(f=script_filename))

        tools.copy_file(template, script_filename)

    def run_post_steps(self):
        """
        Run 'post' compilation steps for component.
        """
        os.chdir(self.component_data_dict["extracted_directory"])

        # Run post steps if any
        if self.component_data_dict["post"] is not None:
            self.run_extra_steps(stepname="post",
                                 run_directory=self.component_data_dict["build_directory_path"])

    def run_extra_steps(self, stepname, run_directory):
        """
        Run extra steps when building a component.
        'stepname' can be 'previous' or 'post'.
        """
        filename = os.path.join(run_directory, stepname + ".sh")
        self.copy_script_header(filename)

        tools.add_text_to_file(filename, self.component_data_dict[stepname])

        self.run_script(filename, run_directory)

    def run_script(self, filename, run_directory=""):
        """
        Run the script 'filename' from the 'run_directory'.
        """
        # 'self' not available in function parameter so we sanitize here
        if run_directory == "":
            run_directory = self.component_data_dict["build_directory_path"]

        os.chdir(run_directory)

        # Substitute script placeholders before running the script
        self.substitute_script_placeholders(filename)

        printer.substep_info("Running file '{f}'".format(f=os.path.basename(filename)))

        cmd = self.get_command_to_run_script(filename)

        if self.component_data_dict["build_into_chroot"] is False:
            # If we are building from outside, e.g. building 'toolchain',
            # we need to ensure we have the required permission
            tools.set_owner_and_group(filename, self.component_data_dict["run_as_username"])

            # Run program with or without output
            if config.VERBOSE is True:
                tools.run_program_with_output(
                    cmd,
                    username=self.component_data_dict["run_as_username"]
                )
            else:
                tools.run_program_without_output(
                    cmd,
                    username=self.component_data_dict["run_as_username"]
                )
        else:
            tools.run_program_into_chroot(cmd, config.BASE_DIRECTORY)

        # Back to the sources directory
        os.chdir(self.component_data_dict["sources_directory"])

    def clean_workspace(self):
        """
        Clean used workspace to build component.
        """
        os.chdir(self.component_data_dict["sources_directory"])
        msg = "Finished building '{n}'".format(n=self.component_data_dict["show_name"])
        printer.substep_info(msg)


class BaseCompilableComponent(BaseComponent):
    """
    BaseCompilableComponent class.

    Base class for components that need to be compiled.
    """
    def __init__(self, component_data_dict):
        BaseComponent.__init__(self, component_data_dict)

        self.build_directory_name = "build"
        self.buildscript_name = "compile.sh"

    def extract_source_code(self):
        """
        Find and extract source tarball for the component.
        """
        # We look for a tar file
        pattern = "{n}*.tar.*".format(n=self.component_data_dict["package_name"])

        # Use 'package_version' in pattern if it is not None
        if self.component_data_dict["version"] is not None:
            pattern = "{n}*{v}*.tar.*".format(n=self.component_data_dict["package_name"],
                                              v=self.component_data_dict["version"])

        source_code_filename = tools.find_file(self.component_data_dict["sources_directory"],
                                               pattern)

        # Try a second run if 'source_code_filename' is None using only name as pattern.
        if source_code_filename is None:
            pattern = "{n}*.tar.*".format(n=self.component_data_dict["package_name"])
            source_code_filename = tools.find_file(self.component_data_dict["sources_directory"],
                                                   pattern)

        # Try to find a zip file in case the tar file was not found
        if source_code_filename is None:
            pattern = "{n}*.zip*".format(n=self.component_data_dict["package_name"])

            # Use 'package_version' in pattern if it is not None
            if self.component_data_dict["version"] is not None:
                pattern = "{n}*{v}*.zip*".format(n=self.component_data_dict["package_name"],
                                                  v=self.component_data_dict["version"])

            source_code_filename = tools.find_file(self.component_data_dict["sources_directory"],
                                                   pattern)

            # Try a second run if 'source_code_filename' is None using only name as pattern.
            if source_code_filename is None:
                pattern = "{n}*.zip*".format(n=self.component_data_dict["package_name"])
                source_code_filename = tools.find_file(
                    self.component_data_dict["sources_directory"],
                    pattern
                )

        # Give error if None
        if source_code_filename is None:
            msg = "Can't find source code file for '{n}' with pattern: '{p}'"
            msg = msg.format(n=self.component_data_dict["name"], p=pattern)
            printer.error(msg)

        # Extract
        tools.extract(source_code_filename)

        # We get the name of the extracted directory
        pattern = "{n}*".format(n=self.component_data_dict["package_name"])

        # Use 'package_version' in pattern if it is not None
        if self.component_data_dict["version"] is not None:
            pattern = "{n}*{v}*".format(n=self.component_data_dict["package_name"],
                                        v=self.component_data_dict["version"])

        # Find directory using pattern
        self.component_data_dict["extracted_directory"] = tools.find_directory(
            self.component_data_dict["sources_directory"],
            pattern)

        # Try a second run if 'extracted_directory' is None using only name as pattern.
        # If found, get the realpath
        if self.component_data_dict["extracted_directory"] is None:
            pattern = "{n}*".format(n=self.component_data_dict["package_name"])
            self.component_data_dict["extracted_directory"] = tools.find_directory(
                self.component_data_dict["sources_directory"],
                pattern
            )
        else:
            self.component_data_dict["extracted_directory"] = os.path.realpath(
                self.component_data_dict["extracted_directory"]
            )

        # Fail if not found 'extracted_directroy'
        if self.component_data_dict["extracted_directory"] is None:
            msg = "Can't find extracted directory for '{n}' with pattern: '{p}'"
            msg = msg.format(n=self.component_data_dict["name"], p=pattern)
            printer.error(msg)

        # Generate build_dir if necessary.
        if self.component_data_dict["require_build_dir"] is True:
            # Generate and save 'build_directory' path
            value = os.path.realpath(
                os.path.join(
                    self.component_data_dict["extracted_directory"],
                    self.build_directory_name
                )
            )
            tools.add_to_dictionary(self.component_data_dict,
                                    "build_directory_path",
                                    value,
                                    concat=False)

            # Create directory
            tools.create_directory(self.component_data_dict["build_directory_path"])
        else:
            # If not, build component into the extracted directory
            tools.add_to_dictionary(self.component_data_dict,
                                    "build_directory_path",
                                    self.component_data_dict["extracted_directory"],
                                    concat=False)

        # Set directory owner if we are building the 'toolchain'
        if self.component_data_dict["builder_name"] == "toolchain":
            tools.set_recursive_owner_and_group(self.component_data_dict["extracted_directory"],
                                                self.component_data_dict["run_as_username"])

    def apply_patches(self):
        """
        Apply patches to the component's source code.
        """
        cmd = "patch -N -p1 --verbose < {f}"
        # Search a .patch file and apply it
        pattern = "{n}*.patch".format(n=self.component_data_dict["package_name"])
        patch_filename = tools.find_file(self.component_data_dict["sources_directory"], pattern)

        if patch_filename is not None:
            script_filename = os.path.join(self.component_data_dict["extracted_directory"],
                                           "patch.sh")
            # Generate 'patch.sh' script
            self.copy_script_header(script_filename)
            cmd = cmd.format(f=patch_filename)
            tools.add_text_to_file(script_filename, cmd)
            self.run_script(script_filename,
                            run_directory=self.component_data_dict["extracted_directory"])

    def run_previous_steps(self):
        """
        Run 'previous' steps for component.
        """
        # Run previous steps if any
        if self.component_data_dict["previous"] is not None:
            self.run_extra_steps(stepname="previous",
                                 run_directory=self.component_data_dict["extracted_directory"])

        os.chdir(self.component_data_dict["sources_directory"])

    def add_configure_to_buildscript(self):
        """
        Add 'configure' command to component's buildscript.
        """
        if self.component_data_dict["configure"] is not None:
            text = self.component_data_dict["configure"]
            if self.component_data_dict["configure_options"] is not None:
                text = "{c} {co}".format(c=self.component_data_dict["configure"],
                                         co=self.component_data_dict["configure_options"])

            tools.add_text_to_file(self.component_data_dict["buildscript_path"], text)

    def add_make_to_buildscript(self):
        """
        Add 'make' command to component's buildscript.
        """
        if self.component_data_dict["make"] is not None:
            text = self.component_data_dict["make"]
            if self.component_data_dict["make_options"] is not None:
                text = "{m} {mo}".format(m=self.component_data_dict["make"],
                                         mo=self.component_data_dict["make_options"])

            tools.add_text_to_file(self.component_data_dict["buildscript_path"], text)

    def add_tests_to_buildscript(self):
        """
        Add 'test' command to component's buildscripti if 'include_tests' is true.
        """
        if self.component_data_dict["include_tests"] is True:
            if self.component_data_dict["test"] is not None:
                text = self.component_data_dict["test"]
                if self.component_data_dict["test_options"] is not None:
                    text = "{t} {to}".format(t=self.component_data_dict["test"],
                                             to=self.component_data_dict["test_options"])

                tools.add_text_to_file(self.component_data_dict["buildscript_path"], text)

    def add_install_to_buildscript(self):
        """
        Add 'install' command to component's buildscript.
        """
        if self.component_data_dict["install"] is not None:
            text = self.component_data_dict["install"]
            if self.component_data_dict["install_options"] is not None:
                text = "{i} {io}".format(i=self.component_data_dict["install"],
                                         io=self.component_data_dict["install_options"])

            tools.add_text_to_file(self.component_data_dict["buildscript_path"], text)

    def generate_buildscript(self):
        """
        Generate buildscript for component.
        """
        self.component_data_dict["buildscript_path"] = os.path.join(
            self.component_data_dict["build_directory_path"],
            self.buildscript_name)

        self.copy_script_header(self.component_data_dict["buildscript_path"])
        self.add_configure_to_buildscript()
        self.add_make_to_buildscript()
        self.add_tests_to_buildscript()
        self.add_install_to_buildscript()

        # Set owner if running as non privileged user
        if self.component_data_dict["build_into_chroot"] is False:
            tools.set_owner_and_group(self.component_data_dict["buildscript_path"],
                                      self.component_data_dict["run_as_username"])

    def check_compiling_and_linking_functions(self):
        """
        Check compiling and linking functions for the built component.
        """
        pass

    def clean_workspace(self):
        """
        Clean used workspace to build component.
        """
        BaseComponent.clean_workspace(self)
        # Remove extracted directory
        if os.path.exists(self.component_data_dict["extracted_directory"]):
            shutil.rmtree(self.component_data_dict["extracted_directory"])


class BaseSystemConfigurationComponent(BaseComponent):
    """
    BaseSystemConfigurationComponent class.

    Base class for components that only configure the final system and
    do not require compilation steps.
    """
    def __init__(self, component_data_dict):
        BaseComponent.__init__(self, component_data_dict)

        # We do not need to unpack anything, so we ran commands from the 'sources_directory'
        tools.add_to_dictionary(self.component_data_dict,
                                "build_directory_path",
                                self.component_data_dict["sources_directory"],
                                concat=False)

        tools.add_to_dictionary(self.component_data_dict,
                                "extracted_directory",
                                self.component_data_dict["sources_directory"],
                                concat=False)

    def clean_workspace(self):
        """
        Clean used workspace to build component.
        """
        BaseComponent.clean_workspace(self)
        # Remove 'post.sh' file
        filepath = os.path.abspath(os.path.join(self.component_data_dict["build_directory_path"],
                                                "post.sh"))
        if os.path.exists(filepath):
            os.remove(filepath)


class CompilableComponent(BaseCompilableComponent):
    """
    CompilableComponent class.

    Class type to be instaciate for a real 'CompilableComponent'.
    """
    def __init__(self, component_data_dict):
        BaseCompilableComponent.__init__(self, component_data_dict)

    def build(self):
        """
        Build steps for 'CompilableComponents'. Functions can be overwritten in the
        'function.py' file under the component recipe folder.
        If so, arguments are:
            - 'component_data_dict': current component data, which can be accessed and modified.
            - 'parent_function': parent method reference.
        """
        # .- Extract source code
        if hasattr(self.extra_functions, "extract_source_code"):
            self.extra_functions.extract_source_code(self.component_data_dict,
                                                     self.extract_source_code)
        else:
            self.extract_source_code()

        # .- Apply patches
        if hasattr(self.extra_functions, "apply_patches"):
            self.extra_functions.apply_patches(self.component_data_dict,
                                               self.apply_patches)
        else:
            self.apply_patches()

        # .- Run previous steps
        if hasattr(self.extra_functions, "run_previous_steps"):
            self.extra_functions.run_previous_steps(self.component_data_dict,
                                                    self.run_previous_steps)
        else:
            self.run_previous_steps()

        # .- Generate buildscript
        if hasattr(self.extra_functions, "generate_buildscript"):
            self.extra_functions.generate_buildscript(self.component_data_dict,
                                                      self.generate_buildscript)
        else:
            self.generate_buildscript()

        # .- Run buildscript
        if hasattr(self.extra_functions, "run_script"):
            self.extra_functions.run_script(self.component_data_dict,
                                            self.run_script)
        else:
            self.run_script(self.component_data_dict["buildscript_path"])

        # .- Run post steps
        if hasattr(self.extra_functions, "run_post_steps"):
            self.extra_functions.run_post_steps(self.component_data_dict,
                                                self.run_post_steps)
        else:
            self.run_post_steps()


class SystemConfigurationComponent(BaseSystemConfigurationComponent):
    """
    SystemConfigurationComponent class.

    Class type to be instanciate for a real 'SystemConfigurationComponent'.
    """
    def __init__(self, component_data_dict):
        BaseSystemConfigurationComponent.__init__(self, component_data_dict)

    def build(self):
        """
        Build steps for 'SystemConfigurationComponent'. Functions can be overwritten in the
        'function.py' file under the component recipe folder.
        If so, arguments are:
            - 'component_data_dict': current component data, which can be accessed and modified.
            - 'parent_function': parent method reference.
        """
        if hasattr(self.extra_functions, "run_post_steps"):
            self.extra_functions.run_post_steps(self.component_data_dict,
                                                self.run_post_steps)
        else:
            self.run_post_steps()
