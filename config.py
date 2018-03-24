# General options
BASE_DIRECTORY = "/mnt/lfs"
NON_PRIVILEGED_USERNAME = "lfs"

MOUNT_SOURCES_DIRECTORY = True
SOURCES_ORIG_DIRECTORY = "@@LFSBUILDER_SRC_DIRECTORY@@/tmp/sources"

MAKEFLAGS = "--jobs=4"
ROOT_PASSWD = "toor"
LFS_VERSION = "8.2"

RESTORE_XML_BACKUPS = True

GENERATE_IMG_FILE = False
MOUNT_IMG_FILE = False
IMG_FILENAME = "@@LFSBUILDER_SRC_DIRECTORY@@/tmp/LFSBuilder.img"
# 1M: 1 megabyte, 1G: 1 gigabyte
IMG_SIZE = "1M"

# Build components from book or not
CUSTOM_COMPONENTS_TO_BUILD = True
INCLUDE_MESON_BUILD_SYSTEM = False


TIMEZONE = "Europe/Madrid"
PAPER_SIZE = "A4"

ROOT_PARTITION_NAME = "sda"
ROOT_PARTITION_NUMBER = ""
GRUB_ROOT_PARTITION_NAME = "loop0"
GRUB_ROOT_PARTITION_NUMBER = "hd0"

FILESYSTEM_PARTITION_TYPE = "ext4"
SWAP_PARTITION_NAME = ""

ETH0_IP_ADDRESS = "192.168.99.2"
ETH0_GATEWAY_ADDRESS = "192.168.99.1"
ETH0_BROADCAST_ADDRESS = "192.168.99.255"
DOMAIN_NAME = "localdomain"

# OpenNIC DNS servers
DNS_ADDRESS_1 = "52.174.55.168"
DNS_ADDRESS_2 = "31.3.135.232"
HOSTNAME = "lfs"

LANG = "en_US.UTF-8"
LOCALE = "es_ES"
CHARMAP = "UTF-8"

DISTRIBUTION_NAME = "Linux From Scratch"
DISTRIBUTION_VERSION = "8.0 LFSBuilder"
DISTRIBUTION_DESCRIPTION = "Linux From Scratch 8.0 from LFSBuilder"

toolchain_xml_filename = "toolchain_data.xml"
system_xml_filename = "system_data.xml"
configuration_xml_filename = "configuration_data.xml"
blfs_xml_filename = "blfs_data.xml"

REMOVE_REBOOT_COMPONENT = False
MOUNT_SYSTEM_BUILDER_DIRECTORIES = False
