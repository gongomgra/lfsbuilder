"""
actions.py

Custom actions to be called from Cli objects ('cli.py')
"""
import argparse
import config
import tools
import printer


class ModifyBuildersList(argparse.Action):
    """
    ModifyBuildersList

    This class ensures that 'builder_list' passed as arguments are
    valid.
    """
    def __init__(self, *args, **kwargs):
        argparse.Action.__init__(self, *args, **kwargs)
        self.builders_list = []
        self.builders_index_dict = {}
        self.lfs_builders = ["toolchain", "system", "configuration"]

    def __call__(self, parser, namespace, values, option_string=None):
        # Sanitize builders list by converting elements to lowercase
        self.builders_list = [b.lower() for b in values]

        # .- Check there is not any duplicated builder before
        # doing anything else
        self.check_builders_dupes()

        # Set 'config.REMOVE_REBOOT_COMPONENT' if 'configuration'
        # is not the latest builder
        if self.builders_list[-1] != "configuration":
            setattr(config, "REMOVE_REBOOT_COMPONENT", True)

        # Modify builders list by adding 'provider' and
        # 'collectors' builders

        # .- Remove 'provider' if present and ensure it is placed
        # at the beginning of the 'self.builders_list' but only iff
        # 'self.builder_list' is not compound by 'collector' builder
        # alone.
        if self.builders_list != ["collector"]:
            tools.remove_all_and_add_element(self.builders_list,
                                             "provider",
                                             index=0)

        # .- Remove 'collector' if present and ensure it is placed
        # at the end of the 'self.builders_list' but only iff
        # 'self.builder_list' is not compound by 'provider' builder
        # alone.
        if self.builders_list != ["provider"]:
            tools.remove_all_and_add_element(self.builders_list, "collector")

        # Substitute 'lfs' name for its builders component
        tools.substitute_in_list(self.builders_list,
                                 "lfs",
                                 self.lfs_builders)

        # .- Check there is not any duplicated builder after substitutions.
        #    Raise error if so
        self.check_builders_dupes()

        # .- Check we are not trying to run 'blfs' before any 'lfs' component
        self.check_builders_order()

        # Set generated value. 'self.dest' is the argument name 'builders_list'
        setattr(namespace, self.dest, self.builders_list)

    def check_builders_dupes(self, bl=None):
        """
        Check there is no a duplicate builder on 'self.builder_list'
        """
        # 'bl' is not None if we are running this method from 'unittest'
        if bl is not None:
            self.builders_list = bl

        for b in set(self.builders_list):
            if self.builders_list.count(b) > 1:
                msg = "Duplicated builder '{b}' is not allowed".format(b=b)
                printer.error(msg)

    def check_builders_order(self, bl=None):
        """
        Check 'self.builder_list' has a correct order according to:
            - 'blfs' should be last builder on the list
            - 'lfs' builders ('toolchain', 'system', 'configuration') should
                maintain that order if all are present
            - ['toolchain', 'configuration'] order is not allowed
        """
        # 'bl' is not None if we are running this method from 'unittest'
        if bl is not None:
            self.builders_list = bl

        # Get the position number of every builder in the 'self.builders_list'
        self.builders_index_dict = {
            "toolchain": tools.get_element_index(self.builders_list,
                                                 "toolchain",
                                                 not_present=-2),

            "system": tools.get_element_index(self.builders_list,
                                              "system",
                                              not_present=-2),

            "configuration": tools.get_element_index(self.builders_list,
                                                     "configuration",
                                                     not_present=-2),

            "blfs": tools.get_element_index(self.builders_list,
                                            "blfs",
                                            not_present=-1)
        }

        # .- Ensure 'blfs' is present and its 'index' is max
        if self.builders_index_dict["blfs"] != -1 and \
           self.builders_index_dict["blfs"] != max(self.builders_index_dict.values()):
            msg = "You can not build 'blfs' before any of the 'lfs' book's builders"
            printer.error(msg)

        # .- Check present 'lfs' book's builders can be built
        is_toolchain_present = tools.is_element_present(self.builders_list,
                                                        "toolchain")
        is_system_present = tools.is_element_present(self.builders_list,
                                                     "system")
        is_configuration_present = tools.is_element_present(self.builders_list,
                                                            "configuration")

        has_toolchain_min_index = self.builders_index_dict["toolchain"] == min(
            [
                self.builders_index_dict["toolchain"],
                self.builders_index_dict["system"],
                self.builders_index_dict["configuration"]
            ]
        )
        # Would be equal only in case both are not present
        is_system_before_configuration = (
            self.builders_index_dict["system"] <= self.builders_index_dict["configuration"]
        )

        is_lfs_order_valid = tools.check_lfs_builders_order(
            t=is_toolchain_present,
            s=is_system_present,
            c=is_configuration_present,
            m=has_toolchain_min_index,
            la=is_system_before_configuration
        )

        # .- Check provided 'lfs' book's builder order
        if is_lfs_order_valid is False:
            msg = "You are trying to build 'lfs' \
book's builders in a wrong order"
            printer.error(msg)


class SetConfigOption(argparse.Action):
    """
    SetConfigOption

    Set 'config.py' constants from values passed to the CLI interface.
    """
    def __call__(self, parser, namespace, value, option_string=None):
        setattr(config, self.dest.upper(), value)
