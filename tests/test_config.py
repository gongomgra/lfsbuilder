import os
import sys
import unittest

import config

class ConfigTestCase(unittest.TestCase):
    """Test for 'config.py' values"""

    def test_base_directory_is_string(self):
        """\_ check 'config.BASE_DIRECTORY' is string"""

        self.assertIs(type(config.BASE_DIRECTORY), str)
        # end

    def test_charmap_is_string(self):
        """\_ check 'config.CHARMAP' is string"""

        self.assertIs(type(config.CHARMAP), str)
        # end

    def test_console_font_is_string(self):
        """\_ check 'config.CONSOLE_FONT' is string"""

        self.assertIs(type(config.CONSOLE_FONT), str)
        # end

    def test_custom_components_to_build_is_boolean(self):
        """\_ check 'config.CUSTOM_COMPONENTS_TO_BUILD' is boolean"""

        self.assertIs(type(config.CUSTOM_COMPONENTS_TO_BUILD), bool)
        # end

    def test_distribution_description_is_string(self):
        """\_ check 'config.DISTRIBUTION_DESCRIPTION' is string"""

        self.assertIs(type(config.DISTRIBUTION_DESCRIPTION), str)
        # end

    def test_distribution_name_is_string(self):
        """\_ check 'config.DISTRIBUTION_NAME' is string"""

        self.assertIs(type(config.DISTRIBUTION_NAME), str)
        # end

    def test_distribution_version_is_string(self):
        """\_ check 'config.DISTRIBUTION_VERSION' is string"""

        self.assertIs(type(config.DISTRIBUTION_VERSION), str)
        # end

    def test_dns_address_1_is_string(self):
        """\_ check 'config.DNS_ADDRESS_1' is string"""

        self.assertIs(type(config.DNS_ADDRESS_1), str)
        # end

    def test_dns_address_2_is_string(self):
        """\_ check 'config.DNS_ADDRESS_2' is string"""

        self.assertIs(type(config.DNS_ADDRESS_2), str)
        # end

    def test_domain_name_is_string(self):
        """\_ check 'config.DOMAIN_NAME' is string"""

        self.assertIs(type(config.DOMAIN_NAME), str)
        # end

    def test_eth0_broadcast_address_is_string(self):
        """\_ check 'config.ETH0_BROADCAST_ADDRESS' is string"""

        self.assertIs(type(config.ETH0_BROADCAST_ADDRESS), str)
        # end

    def test_eth0_gateway_address_is_string(self):
        """\_ check 'config.ETH0_GATEWAY_ADDRESS' is string"""

        self.assertIs(type(config.ETH0_GATEWAY_ADDRESS), str)
        # end

    def test_eth0_ip_address_is_string(self):
        """\_ check 'config.ETH0_IP_ADDRESS' is string"""

        self.assertIs(type(config.ETH0_IP_ADDRESS), str)
        # end

    def test_eth0_mask_is_string(self):
        """\_ check 'config.ETH0_MASK' is string"""

        self.assertIs(type(config.ETH0_MASK), str)
        # end

    def test_filesystem_partition_type_is_string(self):
        """\_ check 'config.FILESYSTEM_PARTITION_TYPE' is string"""

        self.assertIs(type(config.FILESYSTEM_PARTITION_TYPE), str)
        # end

    def test_generate_data_files_is_boolean(self):
        """\_ check 'config.GENERATE_DATA_FILES' is boolean"""

        self.assertIs(type(config.GENERATE_DATA_FILES), bool)
        # end

    def test_generate_img_file_is_boolean(self):
        """\_ check 'config.GENERATE_IMG_FILE' is boolean"""

        self.assertIs(type(config.GENERATE_IMG_FILE), bool)
        # end

    def test_grub_root_partition_name_is_string(self):
        """\_ check 'config.GRUB_ROOT_PARTITION_NAME' is string"""

        self.assertIs(type(config.GRUB_ROOT_PARTITION_NAME), str)
        # end

    def test_grub_root_partition_number_is_string(self):
        """\_ check 'config.GRUB_ROOT_PARTITION_NUMBER' is string"""

        self.assertIs(type(config.GRUB_ROOT_PARTITION_NUMBER), str)
        # end

    def test_hostname_is_string(self):
        """\_ check 'config.HOSTNAME' is string"""

        self.assertIs(type(config.HOSTNAME), str)
        # end

    def test_img_filename_is_string(self):
        """\_ check 'config.IMG_FILENAME' is string"""

        self.assertIs(type(config.IMG_FILENAME), str)
        # end

    def test_img_size_is_string(self):
        """\_ check 'config.IMG_SIZE' is string"""

        self.assertIs(type(config.IMG_SIZE), str)
        # end

    def test_include_meson_builder_is_boolean(self):
        """\_ check 'config.INCLUDE_MESON_BUILDER' is boolean"""

        self.assertIs(type(config.INCLUDE_MESON_BUILDER), bool)
        # end

    def test_keymap_is_string(self):
        """\_ check 'config.KEYMAP' is string"""

        self.assertIs(type(config.KEYMAP), str)
        # end

    def test_lang_is_string(self):
        """\_ check 'config.LANG' is string"""

        self.assertIs(type(config.LANG), str)
        # end

    def test_lfs_version_is_string(self):
        """\_ check 'config.LFS_VERSION' is string"""

        self.assertIs(type(config.LFS_VERSION), str)
        # end

    def test_locale_is_string(self):
        """\_ check 'config.LOCALE' is string"""

        self.assertIs(type(config.LOCALE), str)
        # end

    def test_makeflags_is_string(self):
        """\_ check 'config.MAKEFLAGS' is string"""

        self.assertIs(type(config.MAKEFLAGS), str)
        # end

    def test_mount_img_file_is_boolean(self):
        """\_ check 'config.MOUNT_IMG_FILE' is boolean"""

        self.assertIs(type(config.MOUNT_IMG_FILE), bool)
        # end

    def test_mount_sources_directory_is_boolean(self):
        """\_ check 'config.MOUNT_SOURCES_DIRECTORY' is boolean"""

        self.assertIs(type(config.MOUNT_SOURCES_DIRECTORY), bool)
        # end

    def test_mount_system_builder_directories_is_boolean(self):
        """\_ check 'config.MOUNT_SYSTEM_BUILDER_DIRECTORIES' is boolean"""

        self.assertIs(type(config.MOUNT_SYSTEM_BUILDER_DIRECTORIES), bool)
        # end

    def test_non_privileged_username_is_string(self):
        """\_ check 'config.NON_PRIVILEGED_USERNAME' is string"""

        self.assertIs(type(config.NON_PRIVILEGED_USERNAME), str)
        # end

    def test_paper_size_is_string(self):
        """\_ check 'config.PAPER_SIZE' is string"""

        self.assertIs(type(config.PAPER_SIZE), str)
        # end

    def test_remove_reboot_component_is_boolean(self):
        """\_ check 'config.REMOVE_REBOOT_COMPONENT' is boolean"""

        self.assertIs(type(config.REMOVE_REBOOT_COMPONENT), bool)
        # end

    def test_restore_xml_backups_is_boolean(self):
        """\_ check 'config.RESTORE_XML_BACKUPS' is boolean"""

        self.assertIs(type(config.RESTORE_XML_BACKUPS), bool)
        # end

    def test_root_partition_name_is_string(self):
        """\_ check 'config.ROOT_PARTITION_NAME' is string"""

        self.assertIs(type(config.ROOT_PARTITION_NAME), str)
        # end

    def test_root_partition_number_is_string(self):
        """\_ check 'config.ROOT_PARTITION_NUMBER' is string"""

        self.assertIs(type(config.ROOT_PARTITION_NUMBER), str)
        # end

    def test_root_passwd_is_string(self):
        """\_ check 'config.ROOT_PASSWD' is string"""

        self.assertIs(type(config.ROOT_PASSWD), str)
        # end

    def test_sources_orig_directory_is_string(self):
        """\_ check 'config.SOURCES_ORIG_DIRECTORY' is string"""

        self.assertIs(type(config.SOURCES_ORIG_DIRECTORY), str)
        # end

    def test_swap_partition_name_is_string(self):
        """\_ check 'config.SWAP_PARTITION_NAME' is string"""

        self.assertIs(type(config.SWAP_PARTITION_NAME), str)
        # end

    def test_systemd_is_boolean(self):
        """\_ check 'config.SYSTEMD' is boolean"""

        self.assertIs(type(config.SYSTEMD), bool)
        # end

    def test_sysv_is_boolean(self):
        """\_ check 'config.SYSV' is boolean"""

        self.assertIs(type(config.SYSV), bool)
        # end

    def test_timezone_is_string(self):
        """\_ check 'config.TIMEZONE' is string"""

        self.assertIs(type(config.TIMEZONE), str)
        # end

    def test_blfs_xml_filename_is_string(self):
        """\_ check 'config.blfs_xml_filename' is string"""

        self.assertIs(type(config.blfs_xml_filename), str)
        # end

    def test_configuration_xml_filename_is_string(self):
        """\_ check 'config.configuration_xml_filename' is string"""

        self.assertIs(type(config.configuration_xml_filename), str)
        # end

    def test_system_xml_filename_is_string(self):
        """\_ check 'config.system_xml_filename' is string"""

        self.assertIs(type(config.system_xml_filename), str)
        # end

    def test_toolchain_xml_filename_is_string(self):
        """\_ check 'config.toolchain_xml_filename' is string"""

        self.assertIs(type(config.toolchain_xml_filename), str)
        # end

    def test_continue_at_is_not_boolean(self):
        """\_ check 'config.CONTINUE_AT' is not boolean"""

        self.assertIsNot(type(config.CONTINUE_AT), bool)
        # end


if __name__ == '__main__':
    unittest.main()
