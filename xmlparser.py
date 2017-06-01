
import xml.etree.ElementTree as ET
import os
import tools
import config

class ShowAllEntities(object):
        def __getitem__(self, key):
            # key is your entity, you can do whatever you want with it here
            return key


class LFSXmlParser(object):

        def __init__(self):
                self.packages_entities_file = "packages.ent"
                self.general_entities_file = "general.ent"
                self.toolchain_index_file = "chapter05.xml"
                self.system_index_file = "chapter06.xml"
                self.toolchain_save_index_file = "toolchain_index.txt"

        def get_component_name(self, component_filename):
                # 'gcc-pass1.xml':     'gcc'
                # 'gcc-pass2.xml':     'gcc2'
                # 'libstdc++.xml':     'libstdcpp'
                return component_filename.replace("-pass1", "").replace("-pass", "").replace("++", "pp").replace(".xml", "")

        def generate_packages_data_dict(self):
                # packages.ent file
                file_text = tools.read_file(self.packages_entities_file)
                data_dict = {}
                for line in file_text.split("\n"):
                        line_fields = line.split(" ")
                        # Valid lines are of form: '<!ENTITY key value>'
                        # so number of fields should be 3
                        if len(line_fields) == 3:
                                # Add to dictionary if key is a version or md5 string
                                if line_fields[1].find("-version") != -1 or \
                                   line_fields[1].find("-md5") != -1:
                                        # data_dict['key'] = value
                                        data_dict[line_fields[1].replace('-', '_')] = line_fields[2].replace('"', '').replace('>', '')

                # general.ent file
                file_text = tools.read_file(self.general_entities_file)
                for line in file_text.split("\n"):
                        line_fields = line.split(" ")
                        # Valid lines are of form: '<!ENTITY key *multiple_spaces* value>'
                        # so number of fields should be 8
                        if len(line_fields) == 8:
                                # Add to dictionary if key is 'min-kernel'
                                if line_fields[1].find("min-kernel") != -1:
                                        # data_dict['key'] = value
                                        data_dict[line_fields[1].replace('-', '_')] = line_fields[7].replace('"', '').replace('>', '')
                # Return generated dictionary
                return data_dict

        def generate_components_filelist_from_index(self, indexfile, exclude=[]):
                components_filelist = []

                # Get component list from chapter index
                file_text = tools.read_file(indexfile)
                for line in file_text.split("\n"):
                        line_fields = line.split(" ")
                        # Valid lines are of form: '<space> <space> <xi:include url file.xml>'
                        # so number of fields should be 5
                        if len(line_fields) == 5:
                                # Add to componentList if file.xml is not any of
                                # the given excludes
                                add = True
                                if tools.is_empty_list(exclude) == False:
                                        for e in exclude:
                                                # If there is a match, do not add it
                                                if line_fields[4].find(e) != -1:
                                                        add = False

                                # If not matched excludes but it is not a XML file, do not add it
                                if add == True and line_fields[4].find(".xml") == -1:
                                                add = False

                                if add == True:
                                        # remove useless data 'href="tcl.xml"/>' to get 'tcl.xml'
                                        c = line_fields[4].replace("href=\"", "").replace("\"/>", "")
                                        components_filelist.append(c)


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
                                                     "@@LFS_REPLACEABLE@@"
                                                     "<screen role=\"nodump\"><userinput>tzselect",
                                                     "<screen role=\"nodump\"><userinput remap=\"notRequired\">tzselect")

                        # 'groff' includes commands that are not necessary in the 'system' step (chapter06)
                        # We remap them to 'notRequired' to avoid it to be included in '_post' steps
                        if component_filename == "groff.xml":
                                new_filename = componentfile_path + ".orig"
                                tools.copy_file(componentfile_path, new_filename)
                                substitution_list = ["<replaceable>&lt;paper_size&gt;</replaceable>",
                                                     "@@LFS_REPLACEABLE@@"

                        # Remove 'literal' subchild so commands waiting the EOF string get properly parsed
                        # Remove replaceable subchild. Necessary to properly set timezone
                        # Remove 'tzselect' command as we do not want it to be run. Use config parameter
                        # old = ["<literal>", "</literal>", "<replaceable>&lt;xxx&gt;</replaceable>"]
                        # new = ["", "", "@@LFS_REPLACEABLE@@"]
                        substitution_list = ["<literal>", "",
                                            "</literal>", ""]

                        tools.substitute_multiple_in_file(componentfile_path, substitution_list)

                        # Create XML parser on every iteration
                        parser = ET.XMLParser()
                        parser.parser.UseForeignDTD(True)
                        parser.entity = ShowAllEntities()
                        etree = ET.ElementTree()
                        xml_tree = etree.parse(componentfile_path, parser=parser)

                        component_name = self.get_component_name(component_filename)

                        tools.add_text_to_file(self.toolchain_save_index_file, component_name)

                        # Do not create build directory by default
                        key = component_name + "_buildDir"
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
                                                        key = component_name + "_buildDir"
                                                        tools.add_to_dictionary(components_dict,
                                                                               key, "1", concat=False)
                                                        continue

                                                # Remove patch calls as we do this step later on
                                                elif subnode.text.find("patch -Np1") != -1:
                                                        continue

                                                else:
                                                        key = component_name + "_previous"


                                        elif attribute == "configure":
                                                key = component_name + "_configure"
                                        elif attribute == "make":
                                                key = component_name + "_make"
                                        elif attribute == "install":
                                                key = component_name + "_install"
                                        elif attribute == "test":
                                                key = component_name + "_test"
                                        elif attribute == "check":
                                                key = component_name + "_check"
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
                                                key = component_name + "_post"

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

                        # Try to add version field
                        key = component_name.replace("1", "").replace("2", "") + "_version"
                        if key in data_dict:
                                ET.SubElement(c, "version").text = data_dict[key]
                        else:
                                ET.SubElement(c, "version")

                        # Try to add md5 field
                        key = component_name.replace("1", "").replace("2", "") + "_md5"
                        if key in data_dict:
                                ET.SubElement(c, "md5").text = data_dict[key]
                        else:
                                ET.SubElement(c, "md5")

                        # Add buildDir field
                        key = component_name + "_buildDir"
                        if key in data_dict:
                                ET.SubElement(c, "buildDir").text = data_dict[key]
                        else:
                                ET.SubElement(c, "buildDir")

                        # Add pre field
                        key = component_name + "_previous"
                        if key in data_dict:
                                ET.SubElement(c, "previous").text = data_dict[key]
                        else:
                                ET.SubElement(c, "previous")


                        # Add configure field
                        key = component_name + "_configure"
                        if key in data_dict:
                                ET.SubElement(c, "configure").text = data_dict[key]
                        else:
                                ET.SubElement(c, "configure")

                        # Add make field
                        key = component_name + "_make"
                        if key in data_dict:
                                ET.SubElement(c, "make").text = data_dict[key]
                        else:
                                ET.SubElement(c, "make")

                        # Add install field
                        key = component_name + "_install"
                        if key in data_dict:
                                ET.SubElement(c, "install").text = data_dict[key]
                        else:
                                ET.SubElement(c, "install")

                        # Add test field
                        key = component_name + "_test"
                        if key in data_dict:
                                ET.SubElement(c, "test").text = data_dict[key]
                        else:
                                ET.SubElement(c, "test")

                        # Add post field
                        key = component_name + "_post"
                        if key in data_dict:
                                ET.SubElement(c, "post").text = data_dict[key]
                        else:
                                ET.SubElement(c, "post")

                # Write result
                tools.write_xmlfile(filename, ET.tostring(root))

                # Substitute 'util-linux-version' parameter first to avoid errors
                tools.substitute_in_file(filename,
                                        "util-linux-version", data_dict["util_linux_version"])

                for key in data_dict:
                        if key.find("_version") != -1:
                                if key.find("gcc") != -1:
                                        tools.substitute_in_file(filename, "gcc-version",
                                                                data_dict[key])
                                else:
                                        tools.substitute_in_file(filename, key.replace("_", "-"),
                                                                data_dict[key])
                # Substitute 'min-kernel' parameter
                tools.substitute_in_file(filename, "min-kernel", data_dict["min_kernel"])

        def generate_toolchain_xmlfile(self):
                packages_data_dict = self.generate_packages_data_dict()
                toolchain_index_path = os.path.abspath(os.path.join("book/chapter05", self.toolchain_index_file))
                exclude = ["introduction", "toolchaintechnotes", "generalinstructions"]
                components_filelist = self.generate_components_filelist_from_index(toolchain_index_path,
                                                                         exclude)
                components_data_dict = self.generate_components_dict(components_filelist, toolchain_index_path)
                toolchain_data_dict = tools.join_dicts(components_data_dict, packages_data_dict)

                # Write commands
                self.write_commands_xmlfile(components_filelist, toolchain_data_dict, config.toolchain_xml_filename)

        def generate_system_xmlfile(self):
                packages_data_dict = self.generate_packages_data_dict()
                system_index_path = os.path.abspath(os.path.join("book/chapter06", self.system_index_file))
                exclude = ["introduction", "pkgmgt", "chroot", "systemd", "dbus", "aboutdebug"]
                components_filelist = self.generate_components_filelist_from_index(system_index_path,
                                                                         exclude)
                components_data_dict = self.generate_components_dict(components_filelist, system_index_path)
                system_data_dict = tools.join_dicts(components_data_dict, packages_data_dict)

                # Write commands
                self.write_commands_xmlfile(components_filelist, system_data_dict, config.system_xml_filename)

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
