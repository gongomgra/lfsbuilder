import os
import sys
import unittest

import tools
import config

class ToolsTestCase(unittest.TestCase):
    """Test for 'tools.py' functions"""

    def setUp(self):
        self.good_list = ["provider",
                         "toolchain",
                         "system",
                         "configuration",
                         "blfs"]

        self.bad_list = ["provider",
                         "toolchain",
                         "configuration",
                         "system",
                         "provider",
                         "blfs"]

        self.dummy_file = "dummy.txt"
        self.dummy_file_backup = "dummy.txt.bck"
        self.text = "Hello"

        self.element_a = "system"
        self.element_b = "word"

        self.no_tag_command = "configure --prefix=/usr"
        self.tag_command = "<userinput>{}".format(self.no_tag_command)
        self.remap_command = "<userinput remap=\"configure\">{}".format(self.no_tag_command)
        self.disabled_command = "<userinput remap=\"lfsbuilder_disabled\">{}".format(self.no_tag_command)

        self.default_comment_symbol = "#"
        self.other_comment_symbol = "//"
        self.default_commented_string = "{cs} {c}".format(cs = self.default_comment_symbol,
                                                        c = self.no_tag_command)

        self.other_commented_string = "{cs} {c}".format(cs = self.other_comment_symbol,
                                                        c = self.no_tag_command)

        self.no_file_error_msg = "'{f}' file do not exists".format(f = self.dummy_file)
        self.file_error_msg = "'{f}' file should not exists".format(f = self.dummy_file)
        self.no_backup_file_error_msg = "'{f}' file do not exists".format(f = self.dummy_file_backup)
        self.file_backup_error_msg = "'{f}' file should not exists".format(f = self.dummy_file_backup)

        # Ensure 'dummy_file' exists in order to run tests
        tools.write_file(self.dummy_file, self.text)

        # end

    def tearDown(self):
        if os.path.exists(self.dummy_file) is True:
            os.remove(self.dummy_file)

        if os.path.exists(self.dummy_file_backup) is True:
            os.remove(self.dummy_file_backup)

        # end

    def test_write_file_function_overwrite(self):
        """\_ check if it is possible to overwrite files"""

        # .- write file
        self.assertIsNone(
            tools.write_file(self.dummy_file, self.text)
            )

        if os.path.exists(self.dummy_file) is False:
            raise Exception(self.no_file_error_msg)

        # end

    def test_read_file_function(self):
        """\_ check it is possible to read files"""

        if os.path.exists(self.dummy_file) is False:
            raise Exception(self.no_file_error_msg)

        # .- read_file
        self.assertIsNotNone(
            tools.read_file(self.dummy_file)
            )

        read_text = tools.read_file(self.dummy_file)
        self.assertEqual(read_text, self.text)
        # end

    def test_add_text_to_file_beginning(self):
        """\_ check we can add text at the beginning of files"""
        text = "previous"
        test_string = "previous\n{t}".format(t=self.text)

        # .- add text
        tools.add_text_to_file(self.dummy_file, text, at_the_beginning = True)

        # .- read file
        read_text = tools.read_file(self.dummy_file)

        self.assertMultiLineEqual(read_text, test_string)
        # end

    def test_add_text_to_file_end(self):
        """\_ check we can add text at the end of files"""
        text = "post"
        test_string = "{t}\npost".format(t=self.text)

        # .- add text
        tools.add_text_to_file(self.dummy_file, text)

        # .- read file
        read_text = tools.read_file(self.dummy_file)

        self.assertMultiLineEqual(read_text, test_string)
        # end


    def test_backup_functions(self):
        """\_ check it is possible to backup files"""

        if os.path.exists(self.dummy_file) is False:
            raise Exception(self.no_file_error_msg)

        # .- backup file
        self.assertIsNone(
            tools.backup_file(self.dummy_file)
            )

        if os.path.exists(self.dummy_file_backup) is False:
            raise Exception(self.no_file_backup_error_msg)

        # end

    def test_restore_function(self):
        """\_ check it is possible to restore files"""

        tools.write_file(self.dummy_file_backup, self.text)

        if os.path.exists(self.dummy_file_backup) is False:
            raise Exception(self.no_file_backup_error_msg)

        # .- restore backup_file
        self.assertIsNone(
            tools.restore_backup_file(self.dummy_file)
            )

        if os.path.exists(self.dummy_file_backup) is True:
            raise Exception(self.file_backup_error_msg)

        # end

    def test_substitute_in_file(self):
        """\_ check it is possible to substitute parameters files"""
        text = "@@LFS_BASE_DIRECTORY@@"

        # .- write file
        tools.write_file(self.dummy_file, text)

        self.assertEqual(tools.read_file(self.dummy_file),
                         text)

        # .- substitute
        tools.substitute_in_file(self.dummy_file, text, config.BASE_DIRECTORY)

        self.assertEqual(tools.read_file(self.dummy_file),
                         config.BASE_DIRECTORY)

        # end

    def test_substitute_in_list(self):
        """\_ check it is possible to make a substitution in a list"""
        copy_list = self.good_list[:]

        tools.substitute_in_list(
                copy_list,
                self.element_a,
                self.element_b
            )

        self.assertIn(self.element_b, copy_list)
        # end

    def test_disable_commands_no_tag(self):
        """\_ check we can disable commands withouth XML tags"""
        test_list = [self.no_tag_command]
        self.assertEqual(
            tools.disable_commands(test_list)[1],
            self.disabled_command
        )

    def test_disable_commands_with_tag(self):
        """\_ check we can disable commands with XML tags"""
        test_list = [self.tag_command]
        self.assertEqual(
            tools.disable_commands(test_list)[1],
            self.disabled_command
        )

    def test_disable_commands_with_remap(self):
        """\_ check we can disable commands with XML remap attribute"""
        test_list = [self.remap_command]
        self.assertEqual(
            tools.disable_commands(test_list)[1],
            self.disabled_command
        )

    def test_comment_out_command_default_symbol(self):
        """\_ check we can comment out commands using the default comment symbol"""
        test_list = [self.no_tag_command]
        self.assertEqual(
            tools.comment_out(test_list)[1],
            self.default_commented_string
        )

    def test_comment_out_command_other_symbol(self):
        """\_ check we can comment out commands using another comment symbol"""
        test_list = [self.no_tag_command]
        self.assertEqual(
            tools.comment_out(
                test_list,
                comment_symbol = self.other_comment_symbol
            )[1],
            self.other_commented_string
        )

    def test_find_file(self):
        """\_ check we can find files"""
        self.assertIsNotNone(
            tools.find_file(
                os.getcwd(),
                self.dummy_file
            )
        )




if __name__ == '__main__':
    unittest.main()
