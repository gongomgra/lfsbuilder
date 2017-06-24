# LFS class
import os
import builders

class LFS(object):

    def __init__ (self, action):
        self.action = action

    def build(self):
        # Create required builder and call its build method
        if self.action == "toolchain":
            t = builders.ToolchainBuilder()
            # Generate 'toolchain' commands XML file
            t.generate_commands_file()
            # Build 'toolchain' using commands in XML file
            t.build()
            # Delete object
            del t

        if self.action == "system":
            s = builders.SystemBuilder()
            # Generate 'system' commands XML file
            s.generate_commands_file()
            # Build 'system' using commands in XML file
            s.build()
            # Delete object
            del s

        if self.action == "configuration":
            c = builders.ConfigurationBuilder()
            # Generate 'configuration' commands XML file
            c.generate_commands_file()
            # Build 'configuration' using commands in XML file
            c.build()
            # Delete object
            del c
