
import os
import sys

import config
import tools
import printer

def build(builder_data_dict, parent_function):
    print "'functions.py' file! This is the '{b}'".format(b=builder_data_dict["show_name"])

    tools.pretty_print(builder_data_dict)

    check_non_privileged_user()
    check_mount_point()
    check_tools_directory(builder_data_dict["tools_directory"])
    give_permission_build_dir()

    # Call parent function
    parent_function()


def check_non_privileged_user():
    # Create the config.NON_PRIVILEGED_USERNAME does not exist
    if tools.check_user_exists(config.NON_PRIVILEGED_USERNAME) == False:
        msg = "User '{user}' expecified in the 'config.NON_PRIVILEGED_USERNAME' \
variable doesn't exist"
        msg = msg.format(user = config.NON_PRIVILEGED_USERNAME)
        printer.error(msg)

        # Create this user and group
        printer.warning("User '{u}' does not exists. Creating it".format(
            u=config.NON_PRIVILEGED_USERNAME))
        cmd = "groupadd {U}".format(u=config.NON_PRIVILEGED_USERNAME)
        tools.run_program_without_output(cmd)

        cmd = "useradd -s /bin/bash -g {u} -m -k /dev/null {u}".format(
            u=config.NON_PRIVILEGED_USERNAME)
        tools.run_program_without_output(cmd)

        printer.info("User '{u}' created".format(u=config.NON_PRIVILEGED_USERNAME))


def check_mount_point():
    if os.path.ismount(config.BASE_DIRECTORY) == True:
        printer.info("Mount point check for '{d}' is ok".format(d=config.BASE_DIRECTORY))
    else:
        printer.error("Mount point check for '{d}' failed".format(d=config.BASE_DIRECTORY))

def check_tools_directory(tools_directory):
    root_tools_directory = os.path.abspath(os.path.join("/", "tools"))

    # Check if toolsDir exists or not
    if os.path.exists(tools_directory) == True and os.path.isdir(tools_directory) == True:
        printer.info("Tools directory '{d}' exists".format(d=tools_directory))
    else:
        printer.warning("Tools directory '{d}' doesn't exists. Creating it".format(d=tools_directory))
        os.mkdir(tools_directory)
        printer.info("Tools directory '{d}' created".format(d=tools_directory))

        # Check the root directory symlink (/tools)
    if os.path.exists(root_tools_directory) == True and os.path.islink(root_tools_directory) == True:
        printer.info("Symlink target '{d}' exists".format(d=root_tools_directory))
    else:
        printer.warning("Symlink target '{d}' doesn't exists. Creating it".format(d=root_tools_directory))
        os.mkdir(root_tools_directory)
        printer.info("Symlink target directory '{d}' created".format(d=root_tools_directory))

    if os.path.realpath(root_tools_directory) == tools_directory:
        printer.info("Symlink target '{dest}' is properly set to '{orig}'".format(
            dest=root_tools_directory,
            orig=tools_directory))
    else:
        printer.warning("Symlink target '{dest}' not set correctly. Creating backup at \'" + root_tools_directoryBck +
                        "\' and creating a correct one")
        os.rename(root_tools_directory, root_tools_directoryBck)
        os.mkdir(root_tools_directory)
        os.symlink(tools_directory, root_tools_directory)
        printer.info("Symlink target \'" + root_tools_directory + "\' created")

def give_permission_build_dir():
    directory_list = ["tools", "sources"]

    # Set owner for the config.BASE_DIRECTORY
    tools.set_owner_and_group(os.path.abspath(config.BASE_DIRECTORY),
                              config.NON_PRIVILEGED_USERNAME)
    msg = "Setting '{user}' as owner/group of the '{directory}' directory"
    msg = msg.format(user = config.NON_PRIVILEGED_USERNAME,
                     directory = config.BASE_DIRECTORY)
    printer.info(msg)

    # Set owner for entries in the 'directory_list'
    for d in directory_list:
        d = os.path.join(config.BASE_DIRECTORY, d)
        tools.set_owner_and_group(d, config.NON_PRIVILEGED_USERNAME)
        msg = "Setting {user} as owner of the {directory} directory"
        msg = msg.format(user = config.NON_PRIVILEGED_USERNAME,
                         directory = d)
        printer.info(msg)
