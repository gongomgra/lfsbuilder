import unittest
import itertools

import actions

class ModifyBuildersListTestCase(unittest.TestCase):
    """Test for 'ModifyBuildersList' class"""

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
        # Generate context manager so we can check the error code
        with self.assertRaises(SystemExit) as context_manager:
            test_function(self.bad_list)

        return context_manager
        # end

    def test_builders_no_dupes(self):
        """\_ check there is no duplicated builder"""
        # Check it does not fail
        self.assertIsNone(
            self.mock.check_builders_dupes(self.good_list))

        # end

    def test_builders_dupes(self):
        """\_ check 'provider' is a duplicated builder"""

        context_manager = self.generate_system_exit_context_manager(
            self.mock.check_builders_dupes)
        # We check returned value is 1 (on error)
        self.assertEqual(context_manager.exception.code, 1)

        # end


    def test_builders_no_order(self):
        """\_ check there is no wrong builders order"""
        # Check it does not fail
        self.assertIsNone(
            self.mock.check_builders_order(self.good_list))

        # end

    def test_builders_order(self):
        """\_ check there is a wrong builder orders"""

        context_manager = self.generate_system_exit_context_manager(
            self.mock.check_builders_order)
        # We check returned value is 1 (on error)
        self.assertEqual(context_manager.exception.code, 1)

        # end



    def test_lfs_builders_order(self):
        """\_ check the output of the 'check_lfs_builders_order' function is correct"""

        # All combinations between 5 bits with values (0 or 1)
        bits = list(itertools.product([0,1], repeat=5))
        # Expected output
        output = [1,1,1,1,
                  1,1,1,1,
                  1,1,1,1,
                  0,1,0,1,
                  1,1,1,1,
                  0,0,0,0,
                  0,0,1,1,
                  0,0,0,1]

        # Dummy object
        o = actions.ModifyBuildersList(None, None, None, None)

        i = 0
        j = 1

        print "\n| t - s - c - m - l | v "
        print "+-------------------+---"
        for t, s, c, m, l in bits:
            print "| {t} | {s} | {c} | {m} | {l} | {v} ".format(t=t, s=s, c=c, m=m, l=l, v=output[i])
            self.assertEqual(self.mock.check_lfs_builders_order(t, s, c, m, l),
                             bool(output[i]))
            if j == 4:
                print "+-------------------+---"
                j = 0

            i += 1
            j += 1

        # end

if __name__ == '__main__':
    unittest.main()
