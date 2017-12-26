
import os
import shutil
import tools
import config
import printer

class BaseComponent(object):

    def __init__(self, build_action, components_data_dict):
        self.sources_directory = os.path.join(config.BASE_DIRECTORY, "sources")
        self.tools_directory = os.path.join(config.BASE_DIRECTORY, "tools")
        self.build_action = build_action
        self.name = ""
        self.show_name = ""
        self.key_name = ""
        self.package_name = ""
        # self.patchlist = []
        self.components_data_dict = components_data_dict
        self.build_directory = ""
        self.run_as_username = ""
        self.replaceable_placeholder_value = ""
        self.component_substitution_list = ""

    # def __del__(self):
    #     print "Deleted!"

    def set_attributes(self):
        if self.key_name == "":
            self.key_name = self.name

        # Set default 'package_name' if necessary
        if self.package_name == "":
            self.package_name = self.name
#        tools.pretty_print(self.components_data_dict)

        # Set 'run_as_username' attribute
        if self.run_as_username == "":
            self.run_as_username = config.NON_PRIVILEGED_USERNAME

    def build(self):
        pass

    def get_command_to_run_script(self, filename):
        if self.build_action == "toolchain":
            cmd = "env -i bash -x"
        else:
            cmd = "/tools/bin/env -i /tools/bin/bash -x"

        # Remove BASE_DIRECTORY if we are inside the chroot.
        # We are not related to BASE_DIRECTORY anymore
        if self.build_action != "toolchain":
            filename = filename.replace(config.BASE_DIRECTORY, "")

        cmd = cmd + " " + filename
        return cmd

    def substitute_script_placeholders(self, file_path=None):
        # Substitute in buildscript by default
        if file_path is None:
            file_path = self.buildscript_path

        # Generate setenv file path.
        # Remove BASE_DIRECTORY from path if we are not building the 'toolchain'
        setenv_script_path = os.path.join(config.BASE_DIRECTORY, "setenv.sh")

        if self.build_action != "toolchain":
            # If we are into the chroot, setenv.sh is located at root directory (/setenv.sh)
            # so we remove that part of the 'setenv_script_path' variable
            setenv_script_path = setenv_script_path.replace(config.BASE_DIRECTORY, "")

        # Placeholders to substitute
        substitution_list = ["@@LFS_SETENV_FILE@@", setenv_script_path,
                            "@@LFS_COMPONENT_KEYNAME@@", self.key_name,
                            "@@LFS_BUILD_ACTION@@", self.build_action,
                            "&amp;", "&",
                            "&gt;", ">",
                            "&lt;", "<",
                            "&quot;", "\""]

        # Add component substitution list
        if self.component_substitution_list != "":
            substitution_list.extend(self.component_substitution_list)

        # Remove BASE_DIRECTORY if not building 'toolchain'
        if self.build_action != "toolchain":
            substitution_list.extend([config.BASE_DIRECTORY, ""])


        tools.substitute_multiple_in_file(file_path, substitution_list)

        # Check there are not any pending placeholder
        text = tools.read_file(file_path)
        if text.find("@@LFS") != -1:
            printer.error("Found pending placeholder in \'{}\'".format(file_path))

    def write_script_header(self, filename):
        printer.substepInfo("Generating script \'" + filename + "\'")

        text = """#!/bin/bash
# Component keyName: @@LFS_COMPONENT_KEYNAME@@
# Build action: @@LFS_BUILD_ACTION@@
# Load custom environment
. @@LFS_SETENV_FILE@@
"""

        tools.write_file(filename, text)

    def run_post_steps(self):
        os.chdir(self.extracted_directory)

        # Run post steps if any
        key = self.key_name + "_post"
        if self.components_data_dict[key] is not None:
            self.run_extra_steps(stepname="post", run_directory=self.build_directory)

    def run_extra_steps(self, stepname, run_directory):
        filename = os.path.join(run_directory, stepname + ".sh")
        self.write_script_header(filename)

        key = self.key_name + "_" + stepname
        tools.add_text_to_file(filename, self.components_data_dict[key])

        self.run_script(filename, run_directory)


    def run_script(self, filename, run_directory=""):
        # 'self' not available in function parameter so we sanitize here
        if run_directory == "":
            run_directory = self.build_directory

        os.chdir(run_directory)

        # Substitute script placeholders before running the script
        self.substitute_script_placeholders(filename)

        printer.substepInfo("Running file \'" + os.path.basename(filename) + "\'")

        cmd =  self.get_command_to_run_script(filename)

        if self.build_action == "toolchain":
            tools.set_owner_and_group(filename, self.run_as_username)
            tools.run_program_with_output(cmd, username=self.run_as_username)
        else:
            tools.run_program_into_chroot(cmd, config.BASE_DIRECTORY)

        # Back to the sources directory
        os.chdir(self.sources_directory)



    def clean_workspace(self):
        if self.show_name == "":
            self.show_name = self.name

        os.chdir(self.sources_directory)
        printer.substepInfo("Finished building \'" + self.show_name + "\'.")

class CompilableComponent(BaseComponent):

    def __init__(self, build_action, components_data_dict):
        BaseComponent.__init__(self, build_action, components_data_dict)
        self.extracted_directory = ""
        self.build_directory_name = "build"
        self.build_directory = ""
        self.buildscript_name = "compile.sh"
        self.buildscript_path = ""
        self.require_build_directory = ""
        # self.setenv_script = os.path.join(config.BASE_DIRECTORY, "setenv.sh")
        # self.chrootSetenvScript = os.path.join("/", "setenv.sh")
        self.configure_options = ""
        self.make_options = ""
        self.install_options = ""
        self.include_tests = 0
        self.test_options = ""
        self.package_version = None


    def set_attributes(self):
        BaseComponent.set_attributes(self)

        # Check if component will need to create a build directory or not
        self.require_build_directory = self.components_data_dict[self.key_name + "_buildDir"]

        # Set 'package_version' if exist
        key_version = "{key_name}_version".format(key_name = self.key_name)
        if self.components_data_dict[key_version] is not None:
            self.package_version = self.components_data_dict[key_version]

    def build(self):
        self.extract_source_code()
        self.apply_patches()
        self.run_previous_steps()
        self.generate_buildscript()
        self.run_script(self.buildscript_path)
        self.run_post_steps()

    def extract_source_code(self):
        # We look for a tar file
        pattern = self.package_name + "*.tar.*"

        # Use 'package_version' in pattern if it is not None
        if self.package_version is not None:
            pattern = "{name}-{version}*.tar.*".format(name = self.package_name,
                                                       version = self.package_version)

        source_code_filename = tools.find_file(self.sources_directory, pattern)
        if source_code_filename == "":
            printer.error("Can't find source code file for \'" + self.name + "\' with pattern: " + pattern)
        tools.extract(source_code_filename)
        # We get the name of the extracted directory
        pattern = "{name}-{version}".format(name = self.package_name, version = self.package_version)
        self.extracted_directory = os.path.abspath(tools.find_directory(self.sources_directory, pattern))
        if self.extracted_directory == "":
            printer.error("Can't find extracted directory for \'" + self.package_name + "\' with pattern: " + pattern)

        # Generate extractedDir/build/ if necessary.
        if self.require_build_directory == '1':
            self.build_directory = os.path.join(self.extracted_directory, self.build_directory_name)
            tools.create_directory(self.build_directory)
        else:
            # If not, build component into the extracted directory
            self.build_directory = self.extracted_directory

        # Set directory owner if we are building the 'toolchain'
        if self.build_action == "toolchain":
            tools.set_recursive_owner_and_group(self.extracted_directory, config.NON_PRIVILEGED_USERNAME)

    def apply_patches(self):
        # Search a .patch file and apply it
        pattern = self.package_name + "*.patch"
        patch_filename = tools.find_file(self.sources_directory, pattern)

        if len(patch_filename) != 0:
            script_filename = os.path.join(self.extracted_directory, "patch.sh")
            self.write_script_header(script_filename)
            cmd = "patch -N -p1 --verbose < " + patch_filename
            tools.add_text_to_file(script_filename, cmd)
            self.run_script(script_filename, run_directory = self.extracted_directory)


    def run_previous_steps(self):
        # Run previous steps if any
        key = self.key_name + "_previous"
        if self.components_data_dict[key] is not None:
            self.run_extra_steps(stepname="previous", run_directory=self.extracted_directory)

        os.chdir(self.sources_directory)

    def add_configure_to_buildscript(self):
        key = self.key_name + "_configure"
        text = self.components_data_dict[key]
        if text is not None:
            text = text + " " + self.configure_options
            tools.add_text_to_file(self.buildscript_path, text)

    def add_make_to_buildscript(self):
        key = self.key_name + "_make"
        text = self.components_data_dict[key]
        if text is not None:
            text = text + " " + self.make_options
            tools.add_text_to_file(self.buildscript_path, text)

    def add_tests_to_buildscript(self):
        if self.include_tests == 1:
            key = self.key_name + "_test"
            text = self.components_data_dict[key]
            if text is not None:
                text = text + " " + self.test_options
                tools.add_text_to_file(self.buildscript_path, text)

    def add_install_to_buildscript(self):
        key = self.key_name + "_install"
        text = self.components_data_dict[key]
        if text is not None:
            text = text + " " + self.install_options
            tools.add_text_to_file(self.buildscript_path, text)

    def generate_buildscript(self, custom_build_directory=""):
        self.buildscript_path = os.path.join(self.build_directory, self.buildscript_name)

        self.write_script_header(self.buildscript_path)
        self.add_configure_to_buildscript()
        self.add_make_to_buildscript()
        self.add_tests_to_buildscript()
        self.add_install_to_buildscript()

        # Set owner if running as non privileged user
        if self.build_action == "toolchain":
            tools.set_owner_and_group(self.buildscript_path, config.NON_PRIVILEGED_USERNAME)

    def check_compiling_and_linking_functions(self):
        os.chdir(self.build_directory)
        # Creates a shell script to check compiling and linking functions for required components
        filename = os.path.join(self.build_directory, "compilation_linking_check.sh")

        self.write_script_header(filename)

        text = """
echo 'int main(){}' > dummy.c
# Compile
@@LFS_CHECK_COMPILATION_CC_COMMAND@@
# Check output
@@LFS_CHECK_COMPILATION_GREP_COMMAND@@

# result=$?
# if [ $result -eq 0 ]; then
#    echo -e '\e[92m--- Compilation check was OK ---\e[0m'
# else
#    echo -e '\e[91m--- Compilation check was FAILED ---\e[0m'
#    exit 1
# fi

@@LFS_CHECK_COMPILATION_RM_COMMAND@@
"""
        tools.add_text_to_file(filename, text)
        substitution_list = ["@@LFS_CHECK_COMPILATION_CC_COMMAND@@", self.check_cc_command,
                             "@@LFS_CHECK_COMPILATION_GREP_COMMAND@@", self.check_grep_command,
                             "@@LFS_CHECK_COMPILATION_RM_COMMAND@@", self.check_rm_command]

        tools.substitute_multiple_in_file(filename, substitution_list)
        self.run_script(filename)


    def clean_workspace(self):
        BaseComponent.clean_workspace(self)
        # Remove extracted directory
        shutil.rmtree(self.extracted_directory)


class SystemConfigurationComponent(BaseComponent):
    def set_attributes(self):
        BaseComponent.set_attributes(self)

        # We do not need to unpack anything, so we ran commands from the config.BASE_DIRECTORY
        self.build_directory = config.BASE_DIRECTORY
        self.extracted_directory = config.BASE_DIRECTORY

    def build(self):
        self.run_post_steps()


class Binutils(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "binutils"

class Gcc(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "gcc"

        # Check compilation and linking function for 'system' build
        if self.build_action == "system":
            self.check_cc_command = "cc dummy.c -v -Wl,--verbose &amp;&gt; dummy.log"
            self.check_grep_command = """readelf -l a.out | grep ': /lib'
grep -o '/usr/lib.*/crt[1in].*succeeded' dummy.log
grep -B1 '^ /usr/include' dummy.log
grep 'SEARCH.*/usr/lib' dummy.log |sed 's|; |\\n|g'
grep &quot;/lib.*/libc.so.6 &quot; dummy.log
grep -B4 '^ /usr/include' dummy.log
grep found dummy.log
"""
            self.check_rm_command = "rm -v dummy.c a.out dummy.log"

        # Required patch for glibc to compile properly. Add it to gcc previous steps
        # http://stackoverflow.com/questions/15787684/lfs-glibc-compilation-ld-error
        tools.add_to_dictionary(self.components_data_dict,
                               "gcc_previous",
                               "sed -i '/k prot/agcc_cv_libc_provides_ssp=yes' gcc/configure")
        tools.add_to_dictionary(self.components_data_dict,
                               "gcc_previous",
                               "sed -i 's/if \((code.*))\)/if (\&1; \&\& \!DEBUG_INSN_P (insn))/' gcc/sched-deps.c")

    def run_previous_steps(self):
        CompilableComponent.run_previous_steps(self)
        if self.build_action == "toolchain":
            # Previous steps extract 'mpfr', 'gmp' and 'mpc' tarballs as root user. We need to set owner.
            tools.set_recursive_owner_and_group(self.extracted_directory, config.NON_PRIVILEGED_USERNAME)


    def run_post_steps(self):
        if self.build_action == "system":
            # Don't call parent function as the only check it includes in 'post' is already here
            self.check_compiling_and_linking_functions()
        else:
            # Call parent function
            BaseComponent.run_post_steps(self)

    # def extract_source_code(self):
    #     # First run parent method and then extract mpfr, gmp and mpc
    #     BaseComponent.extract_source_code(self)

    #     for moduleName in ["mpfr", "gmp", "mpc"]:
    #         # We look for a tar file
    #         pattern = moduleName + "*.tar.*"
    #         source_code_filename = tools.find_file(self.sources_directory, pattern)
    #         tools.extract(source_code_filename, self.extracted_directory)
    #         # We get the name of the extracted directory inside of the gcc directory
    #         pattern = moduleName + "*"
    #         temporalExtractedDir = tools.find_directory(self.extracted_directory, pattern)
    #         os.rename(temporalExtractedDir, os.path.join(self.extracted_directory, moduleName))


#     def apply_source_code_patches(self):
#         text = """#!/bin/bash
# for file in $(find gcc/config -name linux64.h -o -name linux.h -o -name sysv4.h)
# do
#   cp -uv $file{,.orig}
#   sed -e 's@/lib\(64\)\?\(32\)\?/ld@/tools&@g' \
#       -e 's@/usr@/tools@g' $file.orig > $file
#   echo '
# #undef STANDARD_STARTFILE_PREFIX_1
# #undef STANDARD_STARTFILE_PREFIX_2
# #define STANDARD_STARTFILE_PREFIX_1 "/tools/lib/"
# #define STANDARD_STARTFILE_PREFIX_2 ""' >> $file
#   touch $file.orig
# done

# sed -i '/k prot/agcc_cv_libc_provides_ssp=yes' gcc/configure
# """
#         filename = os.path.join(self.extracted_directory, "patch.sh")
#         tools.writeFi_pe(filename, text)
#         cmd = "bash" + " " + filename
#         os.chdir(self.extracted_directory)
#         printer.info("Applying patches")
#         tools.run_program_with_output(cmd)
#         os.chdir(self.sources_directory)

class Linuxapiheaders(CompilableComponent):
    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "linux"
        self.key_name = "linux-headers"
        self.show_name = "linuxApiHeaders"
#        self.require_build_directory = 0

#     def generate_buildscript(self):
#         # File to generate extractedDir/compile.sh
#         self.buildscript_path = os.path.join(self.extracted_directory, self.buildscript_name)
#         self.writeBuildScriptHeader()

#         text = """make mrproper
# make INSTALL_HDR_PATH=dest headers_install
# cp -rv dest/include/* /tools/include
# """
#         tools.add_text_to_file (self.buildscript_path, text)

    # def runBuildScript(self):
    #     self.build_directory = self.extracted_directory
    #     BaseComponent.runBuildScript(self)


class Glibc(CompilableComponent):
    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "glibc"
        self.make_options = "--jobs=1"
        if self.build_action == "system":
            self.component_substitution_list = ["@@LFS_TIMEZONE@@", config.TIMEZONE]
            # self.replaceable_placeholder_value = config.TIMEZONE
            # self.confi_oure_options = self.configure_options + "--host=$LFS_TGT --build=$(../scripts/config.guess) --enable-kernel=2.6.32 --with-headers=/tools/include libc_cv_forced_unwind=yes libc_cv_c_cleanup=yes"

        # Compilation check
        if self.build_action == "toolchain":
            self.check_cc_command = "$LFS_TGT-gcc dummy.c"
            self.check_grep_command = "readelf -l a.out | grep ': /tools'"
            self.check_rm_command = "rm -v dummy.c a.out"

    def run_post_steps(self):
        if self.build_action == "toolchain":
            self.check_compiling_and_linking_functions()

        # Call parent function
        BaseComponent.run_post_steps(self)


class Libstdcplusplus(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "libstdcpp"
        # Libstdc++ source files are gcc, but we have to use libstdc++ compile options
        self.package_name = "gcc"
        # self.key_name = "libstdcpp"
        # self.show_name = "libstdc++"
#        self.configure_options = self.configure_options + "--host=$LFS_TGT --disable-multilib --disable-nls --disable-libstdcxx-threads --disable-libstdcxx-pch --with-gxx-include-dir=/tools/$LFS_TGT/include/c++/6.2.0"

    # def addExtraStepsToBuildScript(self):
    #     old = "configure"
    #     new = "libstdc++-v3/configure"
    #     tools.substituteInFile(self.buildscript_path, old, new)

    # def extract_source_code(self):
    #     # First run parent method and then extract mpfr, gmp and mpc
    #     CompilableComponent.extract_source_code(self)

    #     for moduleName in ["mpfr", "gmp", "mpc"]:
    #         # We look for a tar file
    #         pattern = moduleName + "*.tar.*"
    #         source_code_filename = tools.find_file(self.sources_directory, pattern)
    #         tools.extract(source_code_filename, self.extracted_directory)
    #         # We get the name of the extracted directory inside of the gcc directory
    #         pattern = moduleName + "*"
    #         temporalExtractedDir = tools.find_directory(self.extracted_directory, pattern)
    #         os.rename(temporalExtractedDir, os.path.join(self.extracted_directory, moduleName))

    # def extract_source_code(self):
    #     Gcc.extract_source_code(self)

    # def apply_source_code_patches(self):
    #     BaseComponent.apply_source_code_patches(self)

class Binutils2(Binutils):

    def __init__(self, build_action, components_data_dict):
        Binutils.__init__(self, build_action, components_data_dict)
        self.show_name = "binutils2"
        self.key_name ="binutils2"
        self.make_options="--jobs=1"
        # Use 'binutils' component version (usually the same)
        self.package_version = self.components_data_dict["binutils_version"]

        # self.show__oame = "binutils2"
        # self.confi_oure_options = "CC=$LFS_TGT-gcc AR=$LFS_TGT-ar RANLIB=$LFS_TGT-ranlib --prefix=/tools --with-build-sysroot=$LFS --with-sysroot=$LFS --with-lib-path=/tools/lib --disable-nls --disable-werror"

#     def addExtraSteps_poBuildScript(self):
#         text="""
# # Prepare linker for the 'Re-adjusting' phase in a future build
# make -C ld clean
# make -C ld LIB_PATH=/usr/lib:/lib
# cp -v ld/ld-new /tools/bin
# """
#         tools.a_odTextToFile (self.buildscript_path, text)

class Gcc2(Gcc):

    def __init__(self, build_action, components_data_dict):
        Gcc.__init__(self, build_action, components_data_dict)
        self.show_name = "gcc2"
        self.key_name = "gcc2"
        # Use 'gcc' component version (usually the same)
        self.package_version = self.components_data_dict["gcc_version"]

        # Required patch for glibc to compile properly. Add it to gcc2 previous steps
        # http://stackoverflow.com/questions/15787684/lfs-glibc-compilation-ld-error
        tools.add_to_dictionary(self.components_data_dict,
                               "gcc2_previous",
                               "sed -i '/k prot/agcc_cv_libc_provides_ssp=yes' gcc/configure")
        tools.add_to_dictionary(self.components_data_dict,
                               "gcc2_previous",
                               "sed -i 's/if \((code.*))\)/if (\&1; \&\& \!DEBUG_INSN_P (insn))/' gcc/sched-deps.c")


        # Compilation check
        if self.build_action == "toolchain":
            self.check_cc_command = "cc dummy.c"
            self.check_grep_command = "readelf -l a.out | grep ': /tools'"
            self.check_rm_command = "rm -v dummy.c a.out"

    def run_post_steps(self):
        if self.build_action == "toolchain":
            self.check_compiling_and_linking_functions()

        # Call parent function
        BaseComponent.run_post_steps(self)

        #        self.configure_options = "CC=$LFS_TGT-gcc CXX=$LFS_TGT-g++ AR=$LFS_TGT-ar RANLIB=$LFS_TGT-ranlib --prefix=/tools --with-local-prefix=/tools --with-native-system-header-dir=/tools/include --enable-languages=c,c++ --disable-libstdcxx-pch --disable-multilib --disable-bootstrap --disable-libgomp"

#     def apply_source_code_patches(self):

#         text = """#!/bin/bash
# . @@LFS_SETENV_FILE@@
# cat gcc/limitx.h gcc/glimits.h gcc/limity.h > `dirname $($LFS_TGT-gcc -print-libgcc-file-name)`/include-fixed/limits.h
# """
#         filename = os.path.join(self.extracted_directory, "patch2.sh")
#         tools.writeFi_pe(filename, text)
#         # Substitute setenv file path
#         setenv_script = os.path.join(config.BASE_DIRECTORY, "setenv.sh")
#         tools.substituteInFile(filename, "@@LFS_SETENV_FILE@@", setenv_script)

#         cmd = "bash" + " " + filename
#         os.chdir(self.extracted_directory)
#         printer.info("Applying patches \'" + self.show_name + "\'")
#         tools.run_program_with_output(cmd)
#         os.chdir(self.sources_directory)

#         # Run parent class (Gcc) patches
#         Gcc.apply_source_code_patches(self)


#     def addExtraSteps_poBuildScript(self):
#         text="""
# # Create secure symlink. Some programs use 'cc' instead of 'gcc'
# ln -sv gcc /tools/bin/cc
# """
#         tools.a_odTextToFile (self.buildscript_path, text)
#         # Run parent class (Gcc) extra steps
#         Gcc.addExtraSteps_poBuildScript(self)


class Tclcore(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "tcl"
#        self.configure_options = "--prefix=/tools"
#        self.require_build_directory = 0

#     def generate_buildscript(self):
#         # File to generate extractedDir/compile.sh
#         self.buildscript_path = os.path.join(self.extracted_directory, self.buildscript_name)
#         self.writeBuildScriptHeader()

#         text = """cd unix
# ./configure --prefix=/tools
# make
# # Run test suite. Could generate errors. Nevermind
# TZ=UTC make test
# make install

# # Make the installed library writable so debugging symbols can be removed later
# chmod -v u+w /tools/lib/libtcl8.6.so

# # Install TCL headers. 'Expect' package requires them
# make install-private-headers

# # Create a final required symbolic link
# ln -svf tclsh8.6 /tools/bin/tclsh
# """
#         tools.a_odTextToFile (self.buildscript_path, text)

    # def runBuildScript(self):
    #     self.build_directory = self.extracted_directory
    #     CompilableComponent.runBuildScript(self)

class Expect(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "expect"
        self.include_tests = 1

        # self.confi_oure_options = self.configure_options + "--with-tcl=/tools/lib --with-tclinclude=/tools/include"
        # self.install_options = "SCRIPTS=\"\""

#     def apply_source_code_patches(self):
#         text = """#!/bin/bash
# . @@LFS_SETENV_FILE@@
# cp -v configure{,.orig}
# sed 's:/usr/local/bin:/bin:' configure.orig > configure
# """

#         filename = os.path.join(self.extracted_directory, "patch.sh")
#         tools.writeFi_pe(filename, text)
#         # Substitute setenv file path
#         setenv_script = os.path.join(config.BASE_DIRECTORY, "setenv.sh")
#         tools.substituteInFile(filename, "@@LFS_SETENV_FILE@@", setenv_script)

#         cmd = "bash" + " " + filename
#         os.chdir(self.extracted_directory)
#         printer.info("Applying patches")
#         tools.run_program_with_output(cmd)
#         os.chdir(self.sources_directory)

#         # Run parent class (BaseComponent) patches
#         BaseComponent.apply_source_code_patches(self)

#     def add_install_to_buildscript(self):
#         text = "make " + self.install_options + " install"
#         tools.a_odTextToFile(self.buildscript_path, text)


class Dejagnu(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "dejagnu"
        self.show_name = "DejaGNU"
#        self.configure_options = "--prefix=/tools"

    # def add_make_to_buildscript(self):
    #     pass

    # def addExtraSteps_poBuildScript(self):
    #     # Tests should be run after 'make install'
    #     text = "make check"
    #     tools.a_odTextToFile(self.buildscript_path, text)

class Check(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "check"
        # self.confi_oure_options = "PKG_CONFIG= --prefix=/tools"

    # def add_tests_to_buildscript(self):
    #     # Tests are called 'make check' instead
    #     text = "make check"
    #     tools.a_odTextToFile(self.buildscript_path, text)


class Ncurses(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "ncurses"

    def run_post_steps(self):
        if self.build_action == "toolchain":
            CompilableComponent.run_post_steps(self)
        else:
            # If we are building 'system' we have to avoid running this. It tries to compile
            # component twice
            printer.warning("Skipped 'post' steps to avoid building component twice")

#         self.configure_options = self.configure_options + "--with-shared --without-debug --without-ada --enable-widec --enable-overwrite"

#     def apply_source_code_patches(self):
#         text = """#!/bin/bash
# . @@LFS_SETENV_FILE@@
# sed -i s/mawk// configure
# """

#         filename = os.path.join(self.extracted_directory, "patch.sh")
#         tools.writeFi_pe(filename, text)
#         # Substitute setenv file path
#         setenv_script = os.path.join(config.BASE_DIRECTORY, "setenv.sh")
#         tools.substituteInFile(filename, "@@LFS_SETENV_FILE@@", setenv_script)

#         cmd = "bash" + " " + filename
#         os.chdir(self.extracted_directory)
#         printer.info("Applying patches")
#         tools.run_program_with_output(cmd)
#         os.chdir(self.sources_directory)

#         # Run parent class (BaseComponent) patches
#         BaseComponent.apply_source_code_patches(self)


class Bash(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "bash"
        self.include_tests = 1
        # self.confi_oure_options = self.configure_options + "--without-bash-malloc"

#     def addExtraSteps_poBuildScript(self):
#         text = """
# # Make a link for the programs that use sh for a shell
# ln -svf bash /tools/bin/sh
# """
#         tools.a_odTextToFile(self.buildscript_path, text)


class Bzip2(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "bzip2"
#         self.install_options = "PREFIX=/tools"
#         self.require_build_directory = 0

#     def generate_buildscript(self):
#         # File to generate extractedDir/compile.sh
#         self.buildscript_path = os.path.join(self.extracted_directory, self.buildscript_name)
#         self.writeBuildScriptHeader()

#         text = """make
# make PREFIX=/tools install
# """
#         tools.a_odTextToFile (self.buildscript_path, text)


#     def runBuildScript(self):
#         self.build_directory = self.extracted_directory
#         BaseComponent.runBuildScript(self)


class Coreutils(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "coreutils"
        # self.confi_oure_options = self.configure_options + "--enable-install-program=hostname"
        # self.test_options = "RUN_EXPENSIVE_TESTS=yes"
        # self.require_build_directory = 0

    # def add_tests_to_buildscript(self):
    #     # Tests should be run before 'make install'
    #     text = "make RUN_EXPENSIVE_TESTS=yes check"
    #     tools.a_odTextToFile(self.buildscript_path, text)

    def apply_source_code_patches(self):

        if self.build_action == "toolchain":
        # coreutils should not apply patches while building the toolchain
        # reference: http://lfs-support.linuxfromscratch.narkive.com/CLsG3Tyw/5-18-1-coreutils-8-23
            pass
        else:
            CompilableComponent.apply_source_code_patches(self)

    # def generate_buildscript(self):
    #     self.buildscript_path = os.path.join(self.extracted_directory, self.buildscript_name)
    #     self.writeBuildScriptHeader()
    #     self.add_configure_to_buildscript()
    #     self.add_make_to_buildscript()
    #     self.add_install_to_buildscript()

    # def runBuildScript(self):
    #     self.build_directory = self.extracted_directory
    #     BaseComponent.runBuildScript(self)


class Diffutils(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "diffutils"
        # Have issues with 'colors' test (2 != 141) from Python but works properly
        # when running the 'compile.sh' script from terminal
        # https://vendor2.nginfotpdx.net/gitlab/upstream/diffutils/commit/17e2698bcbee30a6cc282d61ad6242a64ba9c7cf
        # Diffutils 3.5
        self.include_tests = 0

class File(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "file"
        self.include_tests = 1

class Findutils(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "findutils"
        self.include_tests = 1
        # Tests never end when running in parallel
        self.test_options = "--jobs=1"


class Gawk(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "gawk"
        # Found errors running tests for toolchain in version 4.1.4. According to the link below,
        # it is ok to keep going if both gcc and binutils sanity checks were ok
        # http://www.linuxquestions.org/questions/linux-from-scratch-13/error-while-running-test-suite-of-gawk-4-1-1-lfsv7-6-a-4175524586/
        self.include_tests = 0

class Gettext(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "gettext"
        # self.require_build_directory = 0

#     def generate_buildscript(self):
#         # File to generate extractedDir/compile.sh
#         self.buildscript_path = os.path.join(self.extracted_directory, self.buildscript_name)
#         self.writeBuildScriptHeader()

#         text = """cd gettext-tools
# EMACS="no" ./configure --prefix=/tools --disable-shared
# make -C gnulib-lib
# make -C intl pluralx.c
# make -C src msgfmt
# make -C src msgmerge
# make -C src xgettext
# # Install the msgfmt, msgmerge and xgettext programs
# cp -v src/{msgfmt,msgmerge,xgettext} /tools/bin
# """
#         tools.a_odTextToFile (self.buildscript_path, text)

#     def runBuildScript(self):
#         self.build_directory = self.extracted_directory
#         BaseComponent.runBuildScript(self)

class Grep(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "grep"
        self.include_tests = 1

class Gzip(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "gzip"
        self.include_tests = 1

class M4(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "m4"
        self.include_tests = 1

class Make(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "make"
        # self.confi_oure_options = self.configure_options + "--without-guile"
        self.include_tests = 1

class Patch(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "patch"
        self.include_tests = 1

class Perl(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "perl"
        # self.require_build_directory = 0

#     def generate_buildscript(self):
#         # File to generate extractedDir/compile.sh
#         self.buildscript_path = os.path.join(self.extracted_directory, self.buildscript_name)
#         self.writeBuildScriptHeader()

#         text = """sh Configure -des -Dprefix=/tools -Dlibs=-lm
# make
# # Only a few of the utilities and libraries need to be installed for the toolchain
# cp -v perl cpan/podlators/scripts/pod2man /tools/bin
# mkdir -pv /tools/lib/perl5/5.24.0
# cp -Rv lib/* /tools/lib/perl5/5.24.0
# """
#         tools.a_odTextToFile (self.buildscript_path, text)

#     def runBuildScript(self):
#         self.build_directory = self.extracted_directory
#         BaseComponent.runBuildScript(self)

class Sed(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "sed"
        self.include_tests = 1

class Tar(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "tar"
        self.include_tests = 1

class Texinfo(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "texinfo"
        self.include_tests = 1

class Utillinux(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "util-linux"
        self.show_name = "UtilLinux"
        # Include tests for 'system' step to avoid issues running 'post.sh'
        if self.build_action == "system":
            self.include_tests = 1

class Xz(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "xz"
        self.include_tests = 1


class Stripping(SystemConfigurationComponent):

    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "stripping"
        if self.build_action == "system":
            self.key_name = "strippingagain"

    def run_post_steps(self):
        # According to the link below, not all files can be stripped, so we ignore those errors
        # http://archives.linuxfromscratch.org/mail-archives/lfs-support/2002-July/008317.html
        key = self.key_name + "_post"
        newValue = self.components_data_dict[key].replace("/tools/lib/*", "/tools/lib/* || true").replace("/tools/{,s}bin/*", "/tools/{,s}bin/* || true")
        tools.add_to_dictionary(self.components_data_dict, key, newValue, concat=False)

        # run parent method
        SystemConfigurationComponent.run_post_steps(self)

    def get_command_to_run_script(self, filename):
        # According to the link below, not all files can be stripped, so we ignore those errors
        # http://archives.linuxfromscratch.org/mail-archives/lfs-support/2002-July/008317.html
        cmd = SystemConfigurationComponent.get_command_to_run_script(self, filename) + " || true"
        return cmd


class Kernfs(SystemConfigurationComponent):

    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "kernfs"
        # 'kernfs' needs to be built like a toolchain component. That is, from outside the chroot
        self.build_action = "toolchain"
        self.run_as_username = "root"

class Creatingdirs(SystemConfigurationComponent):

    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "creatingdirs"


class Createfiles(SystemConfigurationComponent):

    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "createfiles"

class Adjusting(SystemConfigurationComponent):

    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "adjusting"

class Zlib(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "zlib"

class Gmp(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "gmp"

class Mpfr(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "mpfr"

class Mpc(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "mpc"

class Pkgconfig(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "pkgconfig"
        self.package_name = "pkg-config"

class Attr(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "attr"

class Acl(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "acl"

class Libcap(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "libcap"

class Sed(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "sed"

class Shadow(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "shadow"

class Psmisc(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "psmisc"

class Ianaetc(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "iana-etc"

class Bison(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "bison"

class Flex(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "flex"

class Readline(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "readline"

class Bc(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "bc"

class Libtool(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "libtool"

class Gdbm(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "gdbm"

class Gperf(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "gperf"

class Expat(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "expat"

class Inetutils(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "inetutils"

class Xmlparser(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "xml-parser"
        self.package_name = "XML-Parser"

class Intltool(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "intltool"

class Autoconf(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "autoconf"

class Automake(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "automake"

class Kmod(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "kmod"

class Procps(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "procps"

class E2fsprogs(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "e2fsprogs"

class Groff(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "groff"
        # This package does not support parallel build.
        self.make_options = "--jobs=1"
        self.component_substitution_list = ["@@LFS_PAPER_SIZE@@", config.PAPER_SIZE]

class Grub(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "grub"
        self.component_substitution_list = ["@@LFS_ROOT_PARTITION_NAME@@", config.ROOT_PARTITION_NAME,
                                            "@@LFS_ROOT_PARTITION_NUMBER@@", config.ROOT_PARTITION_NUMBER]

        if self.build_action == "configuration":
            # If we are generating a VM disk (using '/dev/loop', etc... then
            # we have to include '--no-floppy' option to the 'grub-install' commnad
            text = components_data_dict["grub_post"].replace("grub-install", "grub-install --no-floppy")
            tools.add_to_dictionary(components_data_dict, key="grub_post", value=text, concat=False)

class Less(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "less"

class Iproute2(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "iproute2"

class Kbd(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "kbd"

class Libpipeline(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "libpipeline"

class Make(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "make"

class Sysklogd(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "sysklogd"

class Sysvinit(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "sysvinit"

class Eudev(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "eudev"

class Mandb(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "man-db"

class Manpages(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "man-pages"

class Vim(CompilableComponent):

    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "vim"

class Bootscripts(CompilableComponent):
    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "bootscripts"
        self.package_name = "lfs-bootscripts"

class Symlinks(SystemConfigurationComponent):
    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "symlinks"

class Network(SystemConfigurationComponent):
    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "network"
        self.component_substitution_list = ["@@LFS_ETH0_IP_ADDRESS@@", config.ETH0_IP_ADDRESS,
                                            "@@LFS_ETH0_GATEWAY_ADDRESS@@", config.ETH0_GATEWAY_ADDRESS,
                                            "@@LFS_ETH0_BROADCAST_ADDRESS@@", config.ETH0_BROADCAST_ADDRESS,
                                            "@@LFS_HOST_DOMAIN_NAME@@", config.DOMAIN_NAME,
                                            "@@LFS_DNS_ADDRESS_1@@", config.DNS_ADDRESS_1,
                                            "@@LFS_DNS_ADDRESS_2@@", config.DNS_ADDRESS_1,
                                            "@@LFS_HOSTNAME@@", config.HOSTNAME]

class Usage(SystemConfigurationComponent):
    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "usage"

class Profile(SystemConfigurationComponent):
    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "profile"
        self.component_substitution_list = ["@@LFS_LANG@@", config.LANG]

class Inputrc(SystemConfigurationComponent):
    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "inputrc"

class Etcshells(SystemConfigurationComponent):
    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "etcshells"

class Fstab(SystemConfigurationComponent):
    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "fstab"
        self.component_substitution_list = ["@@LFS_ROOT_PARTITION_NAME@@", config.ROOT_PARTITION_NAME,
                                            "@@LFS_FILESYSTEM_PARTITION_TYPE@@", config.FILESYSTEM_PARTITION_TYPE,
                                            "@@LFS_SWAP_PARTITION_NAME@@", config.SWAP_PARTITION_NAME]

class Openssl(CompilableComponent):
    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "openssl"

class Cacerts(SystemConfigurationComponent):
    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "cacerts"

class Cpio(CompilableComponent):
    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "cpio"

class Kernel(CompilableComponent):
    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "kernel"
        self.package_name = "linux"

    def run_previous_steps(self):
        CompilableComponent.run_previous_steps(self)
        print("Copying custom \'.config\' file")
        tools.copy_file("kernel_config/kernel_config_499",
                        self.extracted_directory + "/.config")


class Busybox(CompilableComponent):
    pass
    # def __init__(self, build_action, components_data_dict):
    #     CompilableComponent.__init__(self, build_action, components_data_dict)
    #     self.name = "busybox"

class Initrd(SystemConfigurationComponent):
    pass
    # def __init__(self, build_action, components_data_dict):
    #     CompilableComponent.__init__(self, build_action, components_data_dict)
    #     self.name = "initrd"

class Wget(CompilableComponent):
    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "wget"

class Openssh(CompilableComponent):
    def __init__(self, build_action, components_data_dict):
        CompilableComponent.__init__(self, build_action, components_data_dict)
        self.name = "openssh"

class Theend(SystemConfigurationComponent):
    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "theend"
        self.component_substitution_list = ["@@LFS_DISTRIBUTION_NAME@@", config.DISTRIBUTION_NAME,
                                            "@@LFS_DISTRIBUTION_VERSION@@", config.DISTRIBUTION_VERSION,
                                            "@@LFS_DISTRIBUTION_DESCRIPTION@@", config.DISTRIBUTION_DESCRIPTION]

class Reboot(SystemConfigurationComponent):
    def __init__(self, build_action, components_data_dict):
        SystemConfigurationComponent.__init__(self, build_action, components_data_dict)
        self.name = "reboot"
        self.build_action = "toolchain"


    # def run_extra_steps(self, stepname, run_directory):
    #     real_root = os.open("/", os.O_RDONLY)
    #     os.chroot("/mnt/gokstad")
    #     os.chdir("/")
    #     # Chrooted environment

    #     BaseComponent.runExtraStepsIntoChroot(self,stepname=stepname, run_directory="/")

    #     # Put statements to be executed as chroot here
    #     os.fchdir(real_root)
    #     os.chroot(".")

    #     # Back to old root
    #     os.close(real_root)


class Test(BaseComponent):

    def __init__(self, build_action, components_data_dict):
        BaseComponent.__init__(self, build_action, components_data_dict)
        self.name = "a"
