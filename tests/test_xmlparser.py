"""
test_xmlparser.py

Unit test for 'xmlparser.py' module.
"""
import unittest

import xmlparser


class XmlParserTestCase(unittest.TestCase):
    """
    Test for 'xmlparser.py' class
    """

    def setUp(self):
        self.mock = xmlparser.LFSXmlParser({"name": "toolchain", "book": "lfs"})

    def tearDown(self):
        del self.mock

    def test_get_component_name_libstdcpp(self):
        """
        .- check we get 'libstdcpp' as 'get_component_name' for input 'libstdc++'
        """
        self.assertEqual(
            self.mock.get_component_name("libstdc++"),
            "libstdcpp"
        )

    def test_get_component_name_gcc(self):
        """
        .- check we get 'gcc' as 'get_component_name' for input 'gcc-pass1'
        """
        self.assertEqual(
            self.mock.get_component_name("gcc-pass1"),
            "gcc"
        )

    def test_get_component_name_gcc2(self):
        """
        .- check we get 'gcc2' as 'get_component_name' for input 'gcc-pass2'
        """
        self.assertEqual(
            self.mock.get_component_name("gcc-pass2"),
            "gcc2"
        )

    def test_get_component_name_util_linux(self):
        """
        .- check we get 'util-linux' as 'get_component_name' for input 'util-linux'
        """
        self.assertEqual(
            self.mock.get_component_name("util-linux"),
            "util-linux"
        )


if __name__ == '__main__':
    unittest.main()
