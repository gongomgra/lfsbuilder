import os
import sys

import config
import tools
import printer

def run_post_steps(component_data_dict, parent_function):

    parent_function()

    # Get required paths
    ssh_filename = os.path.join(
        component_data_dict["lfsbuilder_src_directory"],
        "recipes",
        "components",
        "openssh",
        "files",
        component_data_dict["openssh_public_key_filename"]
    )

    # .- get $HOME directory path
    if component_data_dict["openssh_username"] == "root":
        # It can be dangerous!
        printer.warning("WARNING: will configure SSH access for 'root'")
        home_directory = os.path.join(config.BASE_DIRECTORY, "root")

    elif component_data_dict["openssh_username"] == "config.NON_PRIVILEGED_USERNAME":
        # Update dictionary value
        tools.add_to_dictionary(
            component_data_dict,
            "openssh_username",
            config.NON_PRIVILEGED_USERNAME,
            concat=False
        )
        # Set home directory
        home_directory = os.path.join(
            config.BASE_DIRECTORY,
            "home",
            config.NON_PRIVILEGED_USERNAME
        )

    else:
        home_directory = os.path.join(
            config.BASE_DIRECTORY,
            "home",
            component_data_dict["openssh_username"]
        )

    # .- '$HOME/.ssh' path
    ssh_config_path = os.path.join(home_directory, ".ssh")

    # .- destination file path
    ssh_destination_filename = os.path.join(
        ssh_config_path,
        component_data_dict["openssh_public_key_filename"]
    )

    # .- authorized_keys
    authorized_keys = os.path.join(ssh_config_path, "authorized_keys")

    if os.path.exists(ssh_filename) is False:
        # Do not configure. SSH public key do not exists.
        msg = """WARNING: SSH access will not be configured because \
the provided public key file '{k}' do not exists."""
        msg = msg.format(k=component_data_dict["openssh_public_key_filename"])
        printer.warning(msg)

    elif tools.check_chroot_user_exists(component_data_dict["openssh_username"]) is False:
        # Do not configure. SSH username do not exists.
        msg = """WARNING: SSH access will not be configured because \
the provided username '{u}' do not exists."""
        msg = msg.format(u=component_data_dict["openssh_username"])
        printer.warning(msg)

    elif os.path.exists(home_directory) is False:
        # Do not configure. SSH username's home directory do not exists.
        msg = """WARNING: SSH access will not be configured because \
the home directory '{h}' do not exists."""
        msg = msg.format(h=home_directory)
        printer.warning(msg)

    else:
        msg = "Installing provided SSH public key '{k}' for username '{u}'"
        msg = msg.format(
            k=component_data_dict["openssh_public_key_filename"],
            u=component_data_dict["openssh_username"]
        )
        printer.substep_info(msg)

        # .- create 'ssh_config_path' directory
        tools.create_directory(ssh_config_path)

        # .- copy public key file
        tools.copy_file(
            ssh_filename,
            ssh_destination_filename
        )

        # .- add to authorized keys
        header = "# --- {f} ---".format(f=component_data_dict["openssh_public_key_filename"])
        tools.add_text_to_file(
            authorized_keys,
            header
        )

        tools.add_text_to_file(
            authorized_keys,
            tools.read_file(ssh_filename)
        )

        # .- get 'UID' and 'GID' values to set permission
        etc_passwd_values = tools.get_uid_gid_chroot_username(
            component_data_dict["openssh_username"]
        )

        # .- set 'ssh_config_path' permission
        tools.set_numeric_recursive_owner_and_group(
            ssh_config_path,
            etc_passwd_values["uid"],
            etc_passwd_values["gid"]
        )
