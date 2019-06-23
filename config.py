"""
config.py

LFSBuilder configuration file
Most of the options present here are also available
via command line interface. Command line options take
precedence over these in this file.
"""
# LFSBuilder version
__version__ = "0.1.1"

# Base directory for building LFS system
BASE_DIRECTORY = "/mnt/lfs"

# Name of the unprivileged username to be used
# when building components as non root
NON_PRIVILEGED_USERNAME = "lfs"

# Linux From Scratch version you want to built.
# Should be a string
LFS_VERSION = "8.4"

# Choose if you want to mount the sources directory or not
# Also, configure the path from where it will be mounted.
# You can include the "@@LFSBUILDER_SRC_DIRECTORY@@" placeholder if you
# want to make this path relative to the main lfsbuilder directory
MOUNT_SOURCES_DIRECTORY = True
SOURCES_ORIG_DIRECTORY = "@@LFSBUILDER_SRC_DIRECTORY@@/tmp/sources"

# MAKEFLAGS environment variable
MAKEFLAGS = "--jobs=4"

# 'root' password to be set on the LFS system
ROOT_PASSWD = "toor"

# password for the 'non_privileged_username' username to be set on the LFS system when
# building 'createuser' component.
NON_PRIVILEGED_USERNAME_PASSWD = "password"

# Whether data files should be generated or not.
# Build will fail in case they do not exists under the 'tmp' directory
GENERATE_DATA_FILES = True

# Restore XML files after modification and parse action
RESTORE_XML_BACKUPS = True

# Generate raw '.img' file for building the LFS system inside it.
# It will be mount via 'losetup' command. You can mount
# your own file or system partition on the 'BASE_DIRECTORY' path instead
# It is also configurable via command line.
GENERATE_IMG_FILE = False
MOUNT_IMG_FILE = False
IMG_FILENAME = "@@LFSBUILDER_SRC_DIRECTORY@@/tmp/LFSBuilder.img"
# 1M: 1 megabyte, 1G: 1 gigabyte
# Around 8G are recommended.
IMG_SIZE = "10G"

# Build components from book or not. If not,
# you can define them in the builder recipe file
# under the 'recipes/builders' directory.
# You should set it to 'True' in case you add components not present in
# any of the LFS book builders.
# You can also overwrite the 'get_components_to_build_list()' method
# for the desired builder instead, temporarily set it to 'True',
# call 'parent_function' and then restore original value.
CUSTOM_COMPONENTS_TO_BUILD = False

# Select boot manager
# 'sysv' for sysvinit
# 'systemd' for systemd
SYSV = True
SYSTEMD = False
EXCLUDED_BOOT_MANAGER = None

# Since version '8.2' of the Linux From Scratch book, it is required to build
# 'python', 'ninja' and 'meson' components if you select the 'systemd' boot manager.
# lfsbuilder will return an error message in case you selected 'systemd' but deselected
# this option.
INCLUDE_MESON_BUILDER = False

# Select whether you want to save the 'tools' directory after the
# 'toolchain' builder. Option available as command line argument.
# Output filename will be '{SAVE_TOOLCHAIN_FILENAME}-{date}.tar.gz'
# where '{date}' is of format 'ddmmyy'
SAVE_TOOLCHAIN = False
SAVE_TOOLCHAIN_FILENAME = 'lfsbuilder-toolchain-@@LFS_VERSION@@'

# Indicate if you want to delete the 'tools' directory after the
# 'system' builder. Option available as command line argument.
DELETE_TOOLS = False

# Timezone to be used. You can use the 'tzselect' command to get
# your own value
TIMEZONE = "Europe/Madrid"

# Paper size for the 'PAGE' environment variable when building 'groff'
# PAPER_SIZE = "letter" commonly used in the United States
# PAPER_SIZE = "A4" may be more suitable elsewhere.
PAPER_SIZE = "A4"

# Locale variables. 'UTF-8' encoding options are highly recommended
KEYMAP = "es"
CONSOLE_FONT = "Lat2-Terminus16"
LANG = "en_US.UTF-8"
LOCALE = "en_US"
CHARMAP = "UTF-8"

# 'grub' and 'fstab' installation parameters. Customize with your own values
# in case you are not using the 'GENERATE_IMG_FILE' and 'MOUNT_IMG_FILE' options.
# WARNING: making mistakes on this configuration could completelly break your computer.
ROOT_PARTITION_NAME = "sda"
ROOT_PARTITION_NUMBER = ""
GRUB_ROOT_PARTITION_NAME = "loop0"
GRUB_ROOT_PARTITION_NUMBER = "hd0"

# 'ext4' is recommended
FILESYSTEM_PARTITION_TYPE = "ext4"
# Set it to "" in case you don't have a swap partition
SWAP_PARTITION_NAME = ""

# Networking configuration
ETH0_IP_ADDRESS = "192.168.99.2"
ETH0_GATEWAY_ADDRESS = "192.168.99.1"
ETH0_BROADCAST_ADDRESS = "192.168.99.255"
ETH0_MASK = "24"
DOMAIN_NAME = "localdomain"

# OpenNIC DNS servers
DNS_ADDRESS_1 = "52.174.55.168"
DNS_ADDRESS_2 = "31.3.135.232"

# Hostname for the LFS system
HOSTNAME = "lfs"

# Configure distribution values your output system
DISTRIBUTION_NAME = "Linux From Scratch"
DISTRIBUTION_VERSION = "@@LFS_VERSION@@ LFSBuilder"
DISTRIBUTION_DESCRIPTION = "Linux From Scratch @@LFS_VERSION@@ from LFSBuilder"

# This parameter should always be 'True' because the 'collector' builder
# handle its job instead.
REMOVE_REBOOT_COMPONENT = True

# Check whether we should mount host system '/proc', '/sys', '/dev' and '/run' directories or not
# You should enable this option in case you are starting a build from 'configuration'
# or 'blfs' builders. Available as command line option
MOUNT_SYSTEM_BUILDER_DIRECTORIES = False

# Verbose mode
VERBOSE = True

# Debug scripts. Adds '-x' parameter to the 'runscript_cmd' builder parameter.
# Available as command line option.
DEBUG_SCRIPTS = False

# You can start building from a concrete component of the first builder provided.
# Works only for 'lfs' or 'blfs' builders
CONTINUE_AT = None

# Generated commands files for each builder
TOOLCHAIN_XML_FILENAME = "toolchain_data.xml"
SYSTEM_XML_FILENAME = "system_data.xml"
CONFIGURATION_XML_FILENAME = "configuration_data.xml"
BLFS_XML_FILENAME = "blfs_data.xml"
