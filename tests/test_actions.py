"""
test_actions.py

Unit test for 'actions.py' module.
"""
import unittest

import actions


class ModifyBuildersListTestCase(unittest.TestCase):
    """
    Test for 'ModifyBuildersList' class
    """

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
        # Dummy class to be tested
        self.mock = actions.ModifyBuildersList(None,
                                               None,
                                               None,
                                               None)

    def tearDown(self):
        del self.mock

    def generate_system_exit_context_manager(self, test_function):
        """
        Generate context manager so we can check the error code.
        """
        with self.assertRaises(SystemExit) as context_manager:
            test_function(self.bad_list)

        return context_manager

    def test_builders_no_dupes(self):
        """
        .- check there is no duplicated builder
        """
        # Check it does not fail
        self.assertIsNone(
            self.mock.check_builders_dupes(self.good_list))

    def test_builders_dupes(self):
        """
        .- check 'provider' is a duplicated builder
        """

        context_manager = self.generate_system_exit_context_manager(
            self.mock.check_builders_dupes)
        # We check returned value is 1 (on error)
        self.assertEqual(context_manager.exception.code, 1)

    def test_builders_no_wrong_order(self):
        """
        .- check there is no wrong builders order
        """
        # Check it does not fail
        self.assertIsNone(
            self.mock.check_builders_order(self.good_list))

    def test_builders_wrong_order(self):
        """
        .- check there is a wrong builder orders
        """

        context_manager = self.generate_system_exit_context_manager(
            self.mock.check_builders_order)
        # We check returned value is 1 (on error)
        self.assertEqual(context_manager.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
