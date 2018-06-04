"""
test_downloader.py

Unit test for 'downloader.py' module.
"""
import unittest

import downloader


class DownloaderTestCase(unittest.TestCase):
    """
    Test for 'Downloader' class
    """

    def setUp(self):
        self.mock = downloader.Downloader("blfs")
        # end

    def tearDown(self):
        del self.mock
        # end

    def generate_system_exit_context_manager(self, test_function):
        """
        Generate context manager so we can check the error code.
        """
        with self.assertRaises(SystemExit) as context_manager:
            test_function()

        return context_manager

    def test_blfs_error_download_source(self):
        """
        .- check we can not download source tarballs for 'blfs' book
        """
        context_manager = self.generate_system_exit_context_manager(
            self.mock.download_source)
        # We check returned value is 1 (on error)
        self.assertEqual(context_manager.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
