
import xml.etree.ElementTree as ET
import os
import re as regexp
import tools
import config

class ShowAllEntities(object):
        def __getitem__(self, key):
            # key is your entity, you can do whatever you want with it here
            return "@@" + key + "@@"


class LFSXmlParser(object):

        def __init__(self):
                self.packages_entities_file = "packages.ent"
                self.general_entities_file = "general.ent"
                self.entities_filelists = ["packages.ent", "general.ent"]
                self.book_basedir = os.path.abspath("book")
                self.save_index_file = "index.txt"

        def get_component_name(self, component_filename):
                # 'gcc-pass1.xml':     'gcc'
                # 'gcc-pass2.xml':     'gcc2'
                # 'libstdc++.xml':     'libstdcpp'
                return component_filename.replace("-pass1", "").replace("-pass", "").replace("++", "pp").replace(".xml", "")

        def process_entities(self, string):
                # string = """&savannah;/releases/acl/acl-&acl-version;.src.tar.gz"""
                query = ".*(\&[a-zA-Z0-9\-]*\;)+.*"
                match = regexp.match(query, string)

                # Iterate over the 'string' while matching
                while match:
                        # Get the matched string. 'findall' returns a list
                        found = regexp.findall(query, string)[0]
                        # found = "&acl-version;"
                        aux_value = found.replace("&", "").replace(";", "")
                        # aux_value = "acl-version"
                        value = "@@{}@@".format(aux_value)
                        # value = "@@acl-version@@"
                        # Finally, replace entity
                        string = string.replace(found, value)
                        # Check if there is a new match
                        match = regexp.match(query, string)


                return string

        def generate_entities_data_dict(self):
                data_dict = {}
                for entity_file in self.entities_filelists:
                        file_text = tools.read_file(entity_file)
                        for line in file_text.split("\n"):
                                # Check if 'line' is an ENTITY description line
                                if line.find("ENTITY") != -1:
                                        line_fields = line.split("\"")
                                        # line_fields = ['<!ENTITY attr-size ', '336 KB', '>']
                                        key = line_fields[0].split(" ")[1]
                                        # Process entities in 'value' if any
                                        value = self.process_entities(line_fields[1])
                                        # Add to dictionary
                                        data_dict[key] = value

                # Return generated dictionary
                return data_dict

        def generate_components_filelist_from_index(self, indexfile, exclude=[]):
                components_filelist = []

                # Get component list from chapter index
                file_text = tools.read_file(indexfile)
                for line in file_text.split("\n"):
                        # Valid lines includes text 'xi:include'
                        if line.find("xi:include") != -1:
                                line_fields = line.split("\"")
                                # line_fields = ['  <xi:include xmlns:xi=',
                                #                'http://www.w3.org/2001/XInclude',
                                #                ' href=',
                                #                'introduction.xml',
                                #                '/>']
                                component = line_fields[3]

                                # Add to components_filelist if 'file.xml' is not any of
                                # the given excludes or it is not a XML file
                                add = True

                                # Do not add it if it is not a XML file
                                if component.find(".xml") == -1:
                                        add = False

                                # Do not add 'component' if excluded
                                if(add == True and tools.is_empty_list(exclude) == False):
                                        for e in exclude:
                                                # Do not add it if match
                                                if component.find(e) != -1:
                                                        add = False
                                # Add it
                                if add == True:
                                        components_filelist.append(component)

                return components_filelist

        def generate_components_dict(self, components_filelist, indexfile_path):
                # Generate components_dict from components_filelist
                components_dict = {}
                for component_filename in components_filelist:
                        componentfile_path = os.path.abspath(os.path.join(os.path.dirname(indexfile_path),
                                                                         component_filename))

                        # 'gcc-pass2' includes a compilation test that we will remap to 'check'
                        # to avoid it to be included in '_previous' step
                        if component_filename == "gcc-pass2.xml":
                                new_filename = componentfile_path + ".orig"
                                tools.copy_file(componentfile_path, new_filename)
                                tools.substitute_in_file(componentfile_path, "<userinput>",
                                                        "<userinput remap=\"check\">")

                        # 'strippingagain' includes commands that are not necessary for us.
                        # We will remap them to 'notRequired'
                        # to avoid it to be included in '_post' step
                        if component_filename == "strippingagain.xml":
                                new_filename = componentfile_path + ".orig"
                                tools.copy_file(componentfile_path, new_filename)
                                tools.substitute_in_file(componentfile_path,
                                                         "<screen role=\"nodump\"><userinput>",
                                                         "<screen role=\"nodump\"><userinput remap=\"notRequired\">")

                        # 'glibc' includes commands that are not necessary in the 'system' step (chapter06)
                        # We remap them to 'notRequired' to avoid it to be included in '_post' steps
                        if component_filename == "glibc.xml":
                                new_filename = componentfile_path + ".orig"
                                tools.copy_file(componentfile_path, new_filename)
                                substitution_list = ["<replaceable>&lt;xxx&gt;</replaceable>",
                                                     "@@LFS_REPLACEABLE@@",
                                                     "<screen role=\"nodump\"><userinput>tzselect",
                                                     "<screen role=\"nodump\"><userinput remap=\"notRequired\">tzselect"]

                                tools.substitute_multiple_in_file(componentfile_path, substitution_list)

                        # 'groff' includes commands that are not necessary in the 'system' step chapter06
                        # We remap them to 'notRequired' to avoid it to be included in '_post' steps
                        if component_filename == "groff.xml":
                                new_filename = componentfile_path + ".orig"
                                tools.copy_file(componentfile_path, new_filename)
                                substitution_list = ["<replaceable>&lt;paper_size&gt;</replaceable>",
                                                     "@@LFS_REPLACEABLE@@"]
                                tools.substitute_multiple_in_file(componentfile_path, substitution_list)

                        # 'shadow' includes commands that are not necessary in the 'system' step chapter06
                        # We remap them to 'notRequired' to avoid it to be included in '_post' steps
                        if component_filename == "shadow.xml":
                                new_filename = componentfile_path + ".orig"
                                tools.copy_file(componentfile_path, new_filename)
                                substitution_list = ["<screen role=\"nodump\"><userinput>passwd root</userinput></screen>",
                                                     "<screen role=\"nodump\"><userinput remap=\"notRequired\">passwd root</userinput></screen>"]
                                tools.substitute_multiple_in_file(componentfile_path, substitution_list)


                        # 'vim' includes commands that are not necessary in the 'system' step chapter06
                        # We remap them to 'notRequired' to avoid it to be included in '_post' steps
                        if component_filename == "vim.xml":
                                new_filename = componentfile_path + ".orig"
                                tools.copy_file(componentfile_path, new_filename)
                                substitution_list = ["<screen role=\"nodump\"><userinput>vim -c \':options\'</userinput></screen>",
                                                     "<screen role=\"nodump\"><userinput remap=\"notRequired\">vim -c \':options\'</userinput></screen>"]
                                tools.substitute_multiple_in_file(componentfile_path, substitution_list)


                        # Remove 'literal' subchild so commands waiting the EOF string get properly parsed
                        # Remove replaceable subchild. Necessary to properly set timezone
                        # Remove 'tzselect' command as we do not want it to be run. Use config parameter
                        # old = ["<literal>", "</literal>", "<replaceable>&lt;xxx&gt;</replaceable>"]
                        # new = ["", "", "@@LFS_REPLACEABLE@@"]
                        substitution_list = ["<literal>", "",
                                             "</literal>", ""]

                        # Remove commands that try to run a bash console interactively
                        # 'chroot.xml' and 'revisedchroot.xml' are excluded
                        bash_removes = ["<screen role=\"nodump\"><userinput>exec /bin/bash --login +h</userinput></screen>", "<screen role=\"nodump\"><userinput remap=\"notRequired\">exec /bin/bash --login +h</userinput></screen>",
                                        "<screen role=\"nodump\"><userinput>exec /tools/bin/bash --login +h</userinput></screen>", "<screen role=\"nodump\"><userinput remap=\"notRequired\">exec /tools/bin/bash --login +h</userinput></screen>",
                                        "<screen role=\"nodump\"><userinput>chroot $LFS /tools/bin/env -i            \
    HOME=/root TERM=$TERM PS1='\u:\w\$ ' \
    PATH=/bin:/usr/bin:/sbin:/usr/sbin   \
    /tools/bin/bash --login</userinput></screen>", "<screen role=\"nodump\"><userinput remap=\"notRequired\">chroot $LFS /tools/bin/env -i            \
    HOME=/root TERM=$TERM PS1='\u:\w\$ ' \
    PATH=/bin:/usr/bin:/sbin:/usr/sbin   \
    /tools/bin/bash --login</userinput></screen>"]

                        # Join substitution lists
                        substitution_list.extend(bash_removes)

                        tools.substitute_multiple_in_file(componentfile_path, substitution_list)

                        # Create XML parser on every iteration
                        parser = ET.XMLParser()
                        parser.parser.UseForeignDTD(True)
                        parser.entity = ShowAllEntities()
                        etree = ET.ElementTree()
                        xml_tree = etree.parse(componentfile_path, parser=parser)

                        component_name = self.get_component_name(component_filename)

                        # Save components list to file
                        tools.add_text_to_file(self.save_index_file, component_name)

                        # Do not create build directory by default
                        key = component_name + "-buildDir"
                        tools.add_to_dictionary(components_dict, key, "0")

                        # Check 'screen/userinput' nodes
                        for node in xml_tree.iter('screen'):
                                if node.attrib.get('revision') == "systemd":
                                        # skip systemd by the moment
                                        continue
                                for subnode in node.iter('userinput'):
                                        # Does the 'remap' attribute exists?
                                        # If not, add it to '_previous'
                                        if 'remap' in subnode.attrib:
                                                attribute = subnode.attrib.get('remap')
                                        else:
                                                attribute = ""

                                        if attribute == "pre":
                                                # Check if we have to create a build directory
                                                if subnode.text.find("mkdir -v build") != -1:
                                                        key = component_name + "-buildDir"
                                                        tools.add_to_dictionary(components_dict,
                                                                               key, "1", concat=False)
                                                        continue

                                                # Remove patch calls as we do this step later on
                                                elif subnode.text.find("patch -Np1") != -1:
                                                        continue

                                                else:
                                                        key = component_name + "-previous"


                                        elif attribute == "configure":
                                                key = component_name + "-configure"
                                        elif attribute == "make":
                                                key = component_name + "-make"
                                        elif attribute == "install":
                                                key = component_name + "-install"
                                        elif attribute == "test":
                                                key = component_name + "-test"
                                        elif attribute == "check":
                                                key = component_name + "-check"
                                        elif attribute == "locale-full":
                                                # Do not run the "locale-full" command because
                                                # it is not necessary
                                                continue
                                        elif attribute == "notRequired":
                                                # Do not run the "notRequired" commands because
                                                # it is not necessary
                                                continue
                                        else:
                                                # By default, add it to the post steps.
                                                # Stripping does not have 'remap' attribute
                                                key = component_name + "-post"

                                        # Add the value to dictionary
                                        tools.add_to_dictionary(components_dict, key,
                                                               subnode.text)

                # Return generated dictionary
                return components_dict

        def write_commands_xmlfile(self, components_filelist, data_dict, filename):
                # Write XML file like:
                # <components>
                #  <component name="">
                #   <version>1.0</version>
                #   <buildDir>0</buildDir>
                #   ...
                #  </component>
                # </components>

                # Create new XML tree
                root = ET.Element("components")
                for component_filename in components_filelist:
                        component_name = self.get_component_name(component_filename)
                        c = ET.SubElement(root, "component", name=component_name)

                        # Try to add 'version' field
                        key = component_name.replace("1", "").replace("2", "") + "-version"
                        if key in data_dict:
                                ET.SubElement(c, "version").text = data_dict[key]
                        else:
                                ET.SubElement(c, "version")

                        # Try to add 'md5' field
                        key = component_name.replace("1", "").replace("2", "") + "-md5"
                        if key in data_dict:
                                ET.SubElement(c, "md5").text = data_dict[key]
                        else:
                                ET.SubElement(c, "md5")

                        # Try to add 'url' field
                        key = component_name.replace("1", "").replace("2", "") + "-url"
                        if key in data_dict:
                                ET.SubElement(c, "url").text = data_dict[key]
                        else:
                                ET.SubElement(c, "url")

                        # Add 'buildDir' field
                        key = component_name + "-buildDir"
                        if key in data_dict:
                                ET.SubElement(c, "buildDir").text = data_dict[key]
                        else:
                                ET.SubElement(c, "buildDir")

                        # Add 'pre' field
                        key = component_name + "-previous"
                        if key in data_dict:
                                ET.SubElement(c, "previous").text = data_dict[key]
                        else:
                                ET.SubElement(c, "previous")


                        # Add 'configure' field
                        key = component_name + "-configure"
                        if key in data_dict:
                                ET.SubElement(c, "configure").text = data_dict[key]
                        else:
                                ET.SubElement(c, "configure")

                        # Add 'make' field
                        key = component_name + "-make"
                        if key in data_dict:
                                ET.SubElement(c, "make").text = data_dict[key]
                        else:
                                ET.SubElement(c, "make")

                        # Add 'install' field
                        key = component_name + "-install"
                        if key in data_dict:
                                ET.SubElement(c, "install").text = data_dict[key]
                        else:
                                ET.SubElement(c, "install")

                        # Add 'test' field
                        key = component_name + "-test"
                        if key in data_dict:
                                ET.SubElement(c, "test").text = data_dict[key]
                        else:
                                ET.SubElement(c, "test")

                        # Add 'post' field
                        key = component_name + "-post"
                        if key in data_dict:
                                ET.SubElement(c, "post").text = data_dict[key]
                        else:
                                ET.SubElement(c, "post")

                # Write result
                tools.write_xmlfile(filename, ET.tostring(root))

                # Substitute placeholders
                for key in data_dict:
                        placeholder = "@@{}@@".format(key)
                        tools.substitute_in_file(filename, placeholder,
                                                 data_dict[key])

        def generate_commands_xmlfile(self, stepname, chapters_list=[], exclude=[]):
                components_filelist = []

                # Get general data from '.ent' files
                data_dict = self.generate_entities_data_dict()

                # Get data from every chapter
                for chapter in chapters_list:
                        index_filename = chapter + ".xml"
                        index_path = os.path.abspath(os.path.join(self.book_basedir,
                                                                  chapter, index_filename))

                        # Get components list
                        aux_components_filelist = self.generate_components_filelist_from_index(index_path,
                                                                                               exclude)

                        components_filelist.extend(aux_components_filelist)

                        # Get data from components list
                        components_data_dict = self.generate_components_dict(aux_components_filelist,
                                                                             index_path)
                        # Add obtained data to the 'data_dict'
                        data_dict = tools.join_dicts(data_dict, components_data_dict)


                # Get destination filename
                attribute = "{}_xml_filename".format(stepname)
                destination_filename = getattr(config, attribute)
                self.write_commands_xmlfile(components_filelist, data_dict, destination_filename)

        def generate_dict_from_xmlfile(self, filename):
                data_dict = {}
                parser = ET.XMLParser()
                parser.parser.UseForeignDTD(True)
                parser.entity = ShowAllEntities()
                etree = ET.ElementTree()
                xml_tree = etree.parse(filename, parser=parser)

                # Iterate over 'component' nodes to extract data
                for node in xml_tree.iter('component'):
                        component_name = node.attrib.get('name')
                        for subnode in node:
                                attribute = component_name + "_" + subnode.tag
                                tools.add_to_dictionary(data_dict, attribute,
                                                       subnode.text, concat=False)
                # return generated dictionary
                return data_dict

# lfs = LfsXmlParser()
# #lfs.generate_toolchain_xmlfile()
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(lfs.generate_dict_from_xmlfile("toolchain.xml"))

# del lfs
