
import os
import tools
import config
import printer
import components
import xmlparser

class BaseBuilder(object):

    def __init__(self):
        self.sourcesDir = os.path.join(config.BASE_DIRECTORY, "sources")
        self.toolsDir = os.path.join(config.BASE_DIRECTORY, "tools")
        self.env_PATH_value = "$UNSET_VARIABLE"
        self.components_to_build = []
        self.componentsDataDict = {}
        # self.rootToolsDir = "/tools"
        # self.rootToolsDirBck = "/tools.bck"
        # self.lfsUsername = "lfs"


    def build(self):
        pass

    def create_setenv_script(self):
        filename = os.path.join(config.BASE_DIRECTORY, "setenv.sh")

        text = """# Do not locate and remember (hash) commands as they are looked up for execution
set +h

# Any command which fail will cause the shell script to exit immediately
set -e

# Any command will fail if using any unset variable. For example: "sudo rm -rf /${UNSET_VARIABLE}*"
# won't run "sudo rm /*". It will fail instead
set -u

# Default umask value
umask 022

# LFS mount point
LFS=/mnt/gokstad
export LFS

# LFS custom PATH
PATH=/tools/bin:/bin:/usr/bin
export PATH

# LFS target kernel name
LFS_TGT=$(uname -m)-lfs-linux-gnu
export LFS_TGT

LC_ALL=POSIX
export LC_ALL

# LFS compile core numbers
MAKEFLAGS='--jobs=4'
export MAKEFLAGS

# Terminal has full of colors
TERM=xterm-256color
export TERM

# LFS prebuild GCC
# CC=$LFS_TGT-gcc
# export CC

# LFS prebuild assembler
# AR=$LFS_TGT-ar
# export AR

# LFS prebuild ranlib
# RANLIB=$LFS_TGT-ranlib
# export RANLIB
"""
        # Write file
        tools.write_file(filename, text)

        # Add @@LFS_ parameters to setenv.sh file and do substitutions
        # tools.substitute_multiple_in_file(...)

#     def stripBinaries(self):
#         printer.info("Stripping generated binaries")
#         filename = os.path.join(config.BASE_DIRECTORY, "strip.sh")

#         # According to the link below, not all files can be stripped, so we ignore those errors
#         # http://archives.linuxfromscratch.org/mail-archives/lfs-support/2002-July/008317.html

#         text = """#!/bin/bash
# . @@LFS_SETENV_FILE@@
# strip --strip-debug /tools/lib/* || true
# /usr/bin/strip --strip-unneeded /tools/{,s}bin/* || true
# rm -rvf /tools/{,share}/{info,man,doc}
# """
#         tools.write_file(filename, text)

#         # Substitute setenv file path
#         setenvScript = os.path.join(config.BASE_DIRECTORY, "setenv.sh")
#         tools.substituteInFile(filename, "@@LFS_SETENV_FILE@@", setenvScript)

#         # Run buildScript with a clean environment
#         os.chdir(config.BASE_DIRECTORY)
#         cmd = "env -i bash" + " " + filename
#         printer.info("Running file \'" + filename + "\' with command: \'" + cmd + "\'")
#         # tools.runProgramWithOutput(cmd)
#         tools.runProgramWithoutOutput(cmd)


class ComponentsBuilder(BaseBuilder):

    def __init__(self, xml_filename=""):
        BaseBuilder.__init__(self)
        self.build_action = ""
        self.xml_filename = xml_filename

    def build(self):
        # Create setenv.sh file
        self.create_setenv_script()

        # Generate componentsDataDict from XML file
        lfs = xmlparser.LFSXmlParser()
        self.componentsDataDict = lfs.generate_dict_from_xmlfile(self.xml_filename)
        del lfs

        # Build componentsList
        for component in self.components_to_build:
            os.chdir(self.sourcesDir)
            # Build correct component class name: binutils -> components.Binutils
            component_fullname = "components." + component.capitalize()
            classname = tools.get_class(component_fullname)
            # Instanciate a new classname object
            o = classname(self.build_action, self.componentsDataDict)
            o.set_attributes()

            printer.info("[*] Building component '" + component + "'")
            o.build()

            o.clean_workspace()
            del o


class ToolchainBuilder(ComponentsBuilder):

    def __init__(self):
        # Call inherited method first
        ComponentsBuilder.__init__(self, "toolchain_packages.xml")
        self.build_action = "toolchain"
        self.env_PATH_value = "/tools/bin:/bin:/usr/bin"
        self.components_to_build = ["binutils", "gcc", "linuxapiheaders", "glibc", "libstdcplusplus", "binutils2", "gcc2", "tclcore", "expect", "dejagnu", "check", "ncurses", "bash", "bzip2", "coreutils", "diffutils", "file", "findutils", "gawk", "gettext", "grep", "gzip", "m4", "make", "patch", "perl", "sed", "tar", "texinfo", "utillinux", "xz", "stripping"]

        # self.components_to_build = ["stripping"]

    # def build(self):
    #     # self.checkMountPoint()
    #     # self.checkToolsDirectory()
    #     # Call parent class steps to build component in componentsToBuild list
    #     ComponentsBuilder.buildSteps(self)


    # def checkMountPoint(self):
    #     if os.path.ismount(config.BASE_DIRECTORY) == True:
    #         printer.info("Mount point check for \'" + config.BASE_DIRECTORY + "\' is ok")
    #     else:
    #         printer.error("Mount point check for \'" + config.BASE_DIRECTORY + "\' failed")

    # def checkToolsDirectory(self):

    #     # Check if toolsDir exists or not
    #     if os.path.exists(self.toolsDir) == True and os.path.isdir(self.toolsDir) == True:
    #         printer.info("Tools directory \'" + self.toolsDir + "\' exists")
    #     else:
    #         printer.warning("Tools directory \'" + self.toolsDir + "\' doesn't exists. Creating it")
    #         os.mkdir(self.toolsDir)
    #         printer.info("Tools directory \'" + self.toolsDir + "\' created")

    #     # Check the root directory symlink (/tools)
    #     if os.path.exists(self.rootToolsDir) == True and os.path.islink(self.rootToolsDir) == True:
    #         printer.info("Symlink target \'" + self.rootToolsDir + "\' exists")
    #     else:
    #         printer.warning("Symlink target \'" + self.rootToolsDir + "\' doesn't exists. Creating it")
    #         os.mkdir(self.rootToolsDir)
    #         printer.info("Tools directory \'" + self.toolsDir + "\' created")

    #     if os.path.realpath(self.rootToolsDir) == self.toolsDir:
    #         printer.info("Symlink target \'" + self.rootToolsDir +
    #                      "\' is properly set to \'" + self.toolsDir + "\'")
    #     else:
    #         printer.warning("Symlink target \'" + self.rootToolsDir +
    #                      "\' not set correctly. Creating backup at \'" + self.rootToolsDirBck +
    #                      "\' and creating a correct one")
    #         os.rename(self.rootToolsDir, self.rootToolsDirBck)
    #         os.mkdir(self.rootToolsDir)
    #         os.symlink(self.toolsDir, self.rootToolsDir)
    #         printer.info("Symlink target \'" + self.rootToolsDir + "\' created")


    # def checkLfsUser(self):
    #     exists = tools.checkUserExists(self.lfsUsername)

    #     if exists == True:
    #         printer.info("User \'" + self.lfsUsername + "\' exists")
    #     else:
    #         printer.warning("User \'" + self.lfsUsername + "\' does not exists. Creating it")
    #         cmd = "groupadd " + self.lfsUsername
    #         tools.runProgramWithoutOutput(cmd)
    #         cmd = "useradd -s /bin/bash -g " + self.lfsUsername + " -m -k /dev/null " + self.lfsUsername
    #         tools.runProgramWithoutOutput(cmd)
    #         printer.info("User \'" + self.lfsUsername + "\' created")


class SystemBuilder(ComponentsBuilder):
    def __init__(self):
        ComponentsBuilder.__init__(self, "system_packages.xml")
        self.build_action = "system"
        self.env_PATH_value = "/bin:/usr/bin:/sbin:/usr/sbin:/tools/bin"
        self.components_to_build = ["kernfs", "creatingdirs", "createfiles", "linuxapiheaders", "man-pages", "glibc", "adjusting", "zlib", "file", "binutils", "gmp", "mpfr", "mpc", "gcc", "bzip2", "pkgconfig", "ncurses", "attr", "acl", "libcap", "sed", "shadow", "psmisc", "iana-etc", "m4", "bison", "flex", "grep", "readline", "bash", "bc", "libtool", "gdbm", "gperf", "expat", "inetutils", "perl", "xml-parser", "intltool", "autoconf", "automake", "xz", "kmod", "gettext", "procps", "e2fsprogs", "coreutils", "diffutils", "gawk", "findutils", "groff", "grub", "less", "gzip", "iproute2", "kbd", "libpipeline", "make", "patch", "sysklogd", "sysvinit", "eudev", "util-linux", "man-db", "tar", "texinfo", "vim", "stripping"]

        self.components_to_build = ["stripping"]

    def buildSteps(self):

        # Call parent class steps to build component in componentsToBuild list
        ComponentsBuilder.buildSteps(self)


        # # Create setenv.sh file
        # self.create_setenv_script()

        # # Generate componentsDataDict from XML file
        # lfs = xmlparser.LfsXmlParser()
        # self.componentsDataDict = lfs.generate_dict_from_xmlfile(self.xml_filename)
        # del lfs

#         self.componentsDataDict = {}
#         key = "fhs_post"
#         value = """
# mkdir -pv /{bin,boot,etc/{opt,sysconfig},home,lib/firmware,mnt,opt}
# exit 1
# mkdir -pv /{media/{floppy,cdrom},sbin,srv,var}
# install -dv -m 0750 /root
# install -dv -m 1777 /tmp /var/tmp
# mkdir -pv /usr/{,local/}{bin,include,lib,sbin,src}
# mkdir -pv /usr/{,local/}share/{color,dict,doc,info,locale,man}
# mkdir -v /usr/{,local/}share/{misc,terminfo,zoneinfo}
# mkdir -v /usr/libexec
# mkdir -pv /usr/{,local/}share/man/man{1..8}
# case $(uname -m) in
# x86_64) ln -sv lib /lib64
# ln -sv lib /usr/lib64
# ln -sv lib /usr/local/lib64 ;;
# esac
# mkdir -v /var/{log,mail,spool}
# ln -sv /run /var/run
# ln -sv /run/lock /var/lock
# mkdir -pv /var/{opt,cache,lib/{color,misc,locate},local}
# """

#      #    value = """pwd
# # ls
# # id"""
#         tools.addToDictionary(self.componentsDataDict, key, value, concat=False)

#         key = "fhs_buildDir"
#         value = "0"
#         tools.addToDictionary(self.componentsDataDict, key, value, concat=False)
#         tools.prettyPrint(self.componentsDataDict)


        # Build componentsList
        # for component in self.components_to_build:
        #     os.chdir(self.sourcesDir)
        #     # Build correct component class name: binutils -> components.Binutils
        #     component_fullname = "components." + component.capitalize()
        #     classname = tools.getClass(component_fullname)
        #     # Instanciate a new classname object
        #     o = classname(config.BASE_DIRECTORY, self.componentsDataDict)
        #     o.setAttributes()
        #     # o.extractSourceCode()
        #     # o.applySourceCodePatches()
        #     # o.generateBuildScript()
        #     # o.runBuildScript()
        #     o.runPostSteps()
        #     # o.cleanWorkspace()
        #     del o
