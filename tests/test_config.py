"""
test_config.py

Unit test for 'config.py' module.
"""
import unittest

import config


class ConfigTestCase(unittest.TestCase):
    """
    Test for 'config.py' values
    """

    def test_base_directory_is_string(self):
        """
        .- check 'config.BASE_DIRECTORY' is string
        """
        self.assertIs(type(config.BASE_DIRECTORY), str)

    def test_charmap_is_string(self):
        """
        .- check 'config.CHARMAP' is string
        """
        self.assertIs(type(config.CHARMAP), str)

    def test_console_font_is_string(self):
        """
        .- check 'config.CONSOLE_FONT' is string
        """
        self.assertIs(type(config.CONSOLE_FONT), str)

    def test_custom_components_to_build_is_boolean(self):
        """
        .- check 'config.CUSTOM_COMPONENTS_TO_BUILD' is boolean
        """
        self.assertIs(type(config.CUSTOM_COMPONENTS_TO_BUILD), bool)

    def test_distribution_description_is_string(self):
        """
        .- check 'config.DISTRIBUTION_DESCRIPTION' is string
        """
        self.assertIs(type(config.DISTRIBUTION_DESCRIPTION), str)

    def test_distribution_name_is_string(self):
        """
        .- check 'config.DISTRIBUTION_NAME' is string
        """
        self.assertIs(type(config.DISTRIBUTION_NAME), str)

    def test_distribution_version_is_string(self):
        """
        .- check 'config.DISTRIBUTION_VERSION' is string
        """
        self.assertIs(type(config.DISTRIBUTION_VERSION), str)

    def test_dns_address_1_is_string(self):
        """
        .- check 'config.DNS_ADDRESS_1' is string
        """
        self.assertIs(type(config.DNS_ADDRESS_1), str)

    def test_dns_address_2_is_string(self):
        """
        .- check 'config.DNS_ADDRESS_2' is string
        """
        self.assertIs(type(config.DNS_ADDRESS_2), str)

    def test_domain_name_is_string(self):
        """
        .- check 'config.DOMAIN_NAME' is string
        """
        self.assertIs(type(config.DOMAIN_NAME), str)

    def test_eth0_broadcast_address_is_string(self):
        """
        .- check 'config.ETH0_BROADCAST_ADDRESS' is string
        """
        self.assertIs(type(config.ETH0_BROADCAST_ADDRESS), str)

    def test_eth0_gateway_address_is_string(self):
        """
        .- check 'config.ETH0_GATEWAY_ADDRESS' is string
        """
        self.assertIs(type(config.ETH0_GATEWAY_ADDRESS), str)

    def test_eth0_ip_address_is_string(self):
        """
        .- check 'config.ETH0_IP_ADDRESS' is string
        """
        self.assertIs(type(config.ETH0_IP_ADDRESS), str)

    def test_eth0_mask_is_string(self):
        """
        .- check 'config.ETH0_MASK' is string
        """
        self.assertIs(type(config.ETH0_MASK), str)

    def test_filesystem_partition_type_is_string(self):
        """
        .- check 'config.FILESYSTEM_PARTITION_TYPE' is string
        """
        self.assertIs(type(config.FILESYSTEM_PARTITION_TYPE), str)

    def test_generate_data_files_is_boolean(self):
        """
        .- check 'config.GENERATE_DATA_FILES' is boolean
        """
        self.assertIs(type(config.GENERATE_DATA_FILES), bool)

    def test_generate_img_file_is_boolean(self):
        """
        .- check 'config.GENERATE_IMG_FILE' is boolean
        """
        self.assertIs(type(config.GENERATE_IMG_FILE), bool)

    def test_grub_root_partition_name_is_string(self):
        """
        .- check 'config.GRUB_ROOT_PARTITION_NAME' is string
        """
        self.assertIs(type(config.GRUB_ROOT_PARTITION_NAME), str)

    def test_grub_root_partition_number_is_string(self):
        """
        .- check 'config.GRUB_ROOT_PARTITION_NUMBER' is string
        """
        self.assertIs(type(config.GRUB_ROOT_PARTITION_NUMBER), str)

    def test_hostname_is_string(self):
        """
        .- check 'config.HOSTNAME' is string
        """
        self.assertIs(type(config.HOSTNAME), str)

    def test_img_filename_is_string(self):
        """
        .- check 'config.IMG_FILENAME' is string
        """
        self.assertIs(type(config.IMG_FILENAME), str)

    def test_img_size_is_string(self):
        """
        .- check 'config.IMG_SIZE' is string
        """
        self.assertIs(type(config.IMG_SIZE), str)

    def test_include_meson_builder_is_boolean(self):
        """
        .- check 'config.INCLUDE_MESON_BUILDER' is boolean
        """
        self.assertIs(type(config.INCLUDE_MESON_BUILDER), bool)

    def test_keymap_is_string(self):
        """
        .- check 'config.KEYMAP' is string
        """
        self.assertIs(type(config.KEYMAP), str)

    def test_lang_is_string(self):
        """
        .- check 'config.LANG' is string
        """
        self.assertIs(type(config.LANG), str)

    def test_lfs_version_is_string(self):
        """
        .- check 'config.LFS_VERSION' is string
        """
        self.assertIs(type(config.LFS_VERSION), str)

    def test_locale_is_string(self):
        """
        .- check 'config.LOCALE' is string
        """
        self.assertIs(type(config.LOCALE), str)

    def test_makeflags_is_string(self):
        """
        .- check 'config.MAKEFLAGS' is string
        """
        self.assertIs(type(config.MAKEFLAGS), str)

    def test_mount_img_file_is_boolean(self):
        """
        .- check 'config.MOUNT_IMG_FILE' is boolean
        """
        self.assertIs(type(config.MOUNT_IMG_FILE), bool)

    def test_mount_sources_directory_is_boolean(self):
        """
        .- check 'config.MOUNT_SOURCES_DIRECTORY' is boolean
        """
        self.assertIs(type(config.MOUNT_SOURCES_DIRECTORY), bool)

    def test_mount_system_builder_directories_is_boolean(self):
        """
        .- check 'config.MOUNT_SYSTEM_BUILDER_DIRECTORIES' is boolean
        """
        self.assertIs(type(config.MOUNT_SYSTEM_BUILDER_DIRECTORIES), bool)

    def test_non_privileged_username_is_string(self):
        """
        .- check 'config.NON_PRIVILEGED_USERNAME' is string
        """
        self.assertIs(type(config.NON_PRIVILEGED_USERNAME), str)

    def test_paper_size_is_string(self):
        """
        .- check 'config.PAPER_SIZE' is string
        """
        self.assertIs(type(config.PAPER_SIZE), str)

    def test_remove_reboot_component_is_boolean(self):
        """
        .- check 'config.REMOVE_REBOOT_COMPONENT' is boolean
        """
        self.assertIs(type(config.REMOVE_REBOOT_COMPONENT), bool)

    def test_restore_xml_backups_is_boolean(self):
        """
        .- check 'config.RESTORE_XML_BACKUPS' is boolean
        """
        self.assertIs(type(config.RESTORE_XML_BACKUPS), bool)

    def test_root_partition_name_is_string(self):
        """
        .- check 'config.ROOT_PARTITION_NAME' is string
        """
        self.assertIs(type(config.ROOT_PARTITION_NAME), str)

    def test_root_partition_number_is_string(self):
        """
        .- check 'config.ROOT_PARTITION_NUMBER' is string
        """
        self.assertIs(type(config.ROOT_PARTITION_NUMBER), str)

    def test_root_passwd_is_string(self):
        """
        .- check 'config.ROOT_PASSWD' is string
        """
        self.assertIs(type(config.ROOT_PASSWD), str)

    def test_sources_orig_directory_is_string(self):
        """
        .- check 'config.SOURCES_ORIG_DIRECTORY' is string
        """
        self.assertIs(type(config.SOURCES_ORIG_DIRECTORY), str)

    def test_swap_partition_name_is_string(self):
        """
        .- check 'config.SWAP_PARTITION_NAME' is string
        """
        self.assertIs(type(config.SWAP_PARTITION_NAME), str)

    def test_systemd_is_boolean(self):
        """
        .- check 'config.SYSTEMD' is boolean
        """
        self.assertIs(type(config.SYSTEMD), bool)

    def test_sysv_is_boolean(self):
        """
        .- check 'config.SYSV' is boolean
        """
        self.assertIs(type(config.SYSV), bool)

    def test_timezone_is_string(self):
        """
        .- check 'config.TIMEZONE' is string
        """
        self.assertIs(type(config.TIMEZONE), str)

    def test_blfs_xml_filename_is_string(self):
        """
        .- check 'config.BLFS_XML_FILENAME' is string
        """
        self.assertIs(type(config.BLFS_XML_FILENAME), str)

    def test_configuration_xml_filename_is_string(self):
        """
        .- check 'config.CONFIGURATION_XML_FILENAME' is string
        """
        self.assertIs(type(config.CONFIGURATION_XML_FILENAME), str)

    def test_system_xml_filename_is_string(self):
        """
        .- check 'config.SYSTEM_XML_FILENAME' is string
        """
        self.assertIs(type(config.SYSTEM_XML_FILENAME), str)

    def test_toolchain_xml_filename_is_string(self):
        """
        .- check 'config.TOOLCHAIN_XML_FILENAME' is string
        """
        self.assertIs(type(config.TOOLCHAIN_XML_FILENAME), str)

    def test_continue_at_is_not_boolean(self):
        """
        .- check 'config.CONTINUE_AT' is not boolean
        """
        self.assertIsNot(type(config.CONTINUE_AT), bool)

    def test_verbose_is_boolean(self):
        """
        .- check 'config.VERBOSE' is boolean
        """
        self.assertIs(type(config.VERBOSE), bool)


if __name__ == '__main__':
    unittest.main()
