
import os
import sys
import shutil

import config
import tools
import printer

def build(builder_data_dict, parent_function):

    check_non_privileged_user()
    check_mount_point()
    check_tools_directory(builder_data_dict["tools_directory"])
    give_permission_build_dir()

    # Call parent function
    parent_function()


def check_non_privileged_user():
    # Create the config.NON_PRIVILEGED_USERNAME does not exist
    if tools.check_user_exists(config.NON_PRIVILEGED_USERNAME) is False:
        msg = "User '{user}' expecified in the 'config.NON_PRIVILEGED_USERNAME' \
variable doesn't exist"
        msg = msg.format(user=config.NON_PRIVILEGED_USERNAME)
        printer.error(msg)

        # Create this user and group
        printer.warning("User '{u}' does not exists. Creating it".format(
            u=config.NON_PRIVILEGED_USERNAME))
        cmd = "groupadd {U}".format(u=config.NON_PRIVILEGED_USERNAME)
        tools.run_program_without_output(cmd)

        cmd = "useradd -s /bin/bash -g {u} -m -k /dev/null {u}"
        cmd = cmd.format(u=config.NON_PRIVILEGED_USERNAME)
        tools.run_program_without_output(cmd)

        printer.info("User '{u}' created".format(u=config.NON_PRIVILEGED_USERNAME))


def check_mount_point():
    if tools.is_mount(config.BASE_DIRECTORY) is True:
        printer.info("Mount point check for '{d}' is ok".format(d=config.BASE_DIRECTORY))
    else:
        printer.error("Mount point check for '{d}' failed".format(d=config.BASE_DIRECTORY))


def check_tools_directory(tools_directory):
    root_tools_directory = os.path.abspath(os.path.join("/", "tools"))
    root_tools_directory_bck = os.path.abspath(os.path.join("/", "tools.bck"))
    create_symlink = True

    # .- Check if tools_directory exists or not
    if os.path.exists(tools_directory) is True and os.path.isdir(tools_directory) is True:
        printer.info("Tools directory '{d}' exists".format(d=tools_directory))
    else:
        msg = "Tools directory '{d}' doesn't exists. Creating it"
        msg = msg.format(d=tools_directory)
        printer.warning(msg)
        os.mkdir(tools_directory)
        printer.info("Tools directory '{d}' created".format(d=tools_directory))

    # .- Check the root directory symlink (/tools)
    if os.path.exists(root_tools_directory) is True:
        printer.info("Symlink target '{d}' exists".format(d=root_tools_directory))
        if os.path.exists(root_tools_directory_bck) is True:
            msg = "Deleting backup directory '{d}'"
            msg = msg.format(d=root_tools_directory_bck)
            printer.warning(msg)
            if os.path.islink(root_tools_directory_bck) is True:
                os.unlink(root_tools_directory_bck)
            elif os.path.isdir(root_tools_directory_bck) is True:
                shutil.rmtree(root_tools_directory_bck)

        # Backup
        msg = "Backing up previous tools directory '{d}' into '{b}'"
        msg = msg.format(d=root_tools_directory, b=root_tools_directory_bck)
        printer.info(msg)
        os.rename(root_tools_directory, root_tools_directory_bck)
        create_symlink = True

    # Is link?
    if os.path.islink(root_tools_directory) is True:
        # Symlink ok?
        if os.path.realpath(root_tools_directory) == os.path.realpath(tools_directory):
            msg = "Symlink target '{dest}' is properly set to '{orig}'"
            msg = msg.format(dest=root_tools_directory, orig=tools_directory)
            printer.info(msg)
            create_symlink = False
        else:
            msg = "Symlink target '{dest}' is not set to '{orig}'. \
                    Backing up previous symlink '{dest}' to '{back}'"
            msg = msg.format(
                dest=root_tools_directory,
                orig=tools_directory,
                back=root_tools_directory_bck
            )
            printer.warning(msg)
            os.rename(root_tools_directory, root_tools_directory_bck)
            create_symlink = True

    # .- Create symlink
    if create_symlink is True:
        msg = "Symlink target '{d}' doesn't exists. Creating it"
        msg = msg.format(d=root_tools_directory)
        printer.warning(msg)
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
        if os.path.exists(d) is True:
            tools.set_owner_and_group(d, config.NON_PRIVILEGED_USERNAME)
            msg = "Setting {user} as owner of the {directory} directory"
            msg = msg.format(user = config.NON_PRIVILEGED_USERNAME,
                             directory = d)
            printer.info(msg)
