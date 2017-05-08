# LFS class
import os

import builders
import xmlparser

class LFS(object):

    def __init__ (self, action):
        self.action = action

    def build(self):
        # Create required builder and call its build method
        if self.action == "toolchain":
            # Generate toolchain commands XML file
            x = xmlparser.LFSXmlParser()
            x.generate_toolchain_xmlfile()
            del x

            # Build toolchain using commands in XML file
            t = builders.ToolchainBuilder()
            t.build()
            del t

        if self.action == "system":
            # Generate system commands XML file
            x = xmlparser.LFSXmlParser()
            x.generate_system_xmlfile()
            del x

            # Build system using commands in XML file
            s = builders.SystemBuilder()
            s.build()
            del s
