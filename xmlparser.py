"""
xmlparser.py

Parse XML files to get book's command and components data.
"""
import xml.etree.ElementTree as ET
import os
import re as regexp

import tools
import config
import printer


class ShowAllEntities(object):
    """
    ShowAllEntities class.

    Process XML entities found while parsing book's XML files.
    """
    def __getitem__(self, key):
        # key is the XML entity, we can do whatever you want with it here
        return tools.generate_placeholder(key)


class LFSXmlParser(object):
    """
    LFSXmlParser class.

    Parse book's XML files.
    """
    def __init__(self, builder_data_dict=None):
        if builder_data_dict is None:
            self.builder_data_dict = {"book": "lfs"}

        self.temporal_folder = os.path.abspath("tmp")

        self.builder_data_dict = tools.join_dicts({}, builder_data_dict)

        self.book_basedir = os.path.abspath(os.path.join(self.temporal_folder,
                                                         self.builder_data_dict["book"]))

        self.packages_entities_file = os.path.abspath(os.path.join(self.book_basedir,
                                                                   "packages.ent"))

        self.general_entities_file = os.path.abspath(os.path.join(self.book_basedir,
                                                                  "general.ent"))

        self.entities_filelist = [self.packages_entities_file, self.general_entities_file]

        self.save_index_file = os.path.abspath(os.path.join(self.temporal_folder,
                                                            "{b}_components_to_build.txt"))
        self.save_index_file = self.save_index_file.format(b=self.builder_data_dict["name"])

        self.extra_functions = None

        self.xml_attributes_list = ["version", "md5", "url", "require_build_dir", "previous",
                                    "configure", "make", "test", "install", "post"]

    def get_component_name(self, component_filename):
        """
        Return component name from 'component_filename'.
        'gcc-pass1.xml':     'gcc'
        'gcc-pass2.xml':     'gcc2'
        'libstdc++.xml':     'libstdcpp'
        """
        return (
            component_filename
            .replace("-pass1", "")
            .replace("-pass", "")
            .replace("++", "pp")
            .replace(".xml", "")
        )

    def process_entities(self, string):
        """
        Process XML entities present into 'string'.
        """
        # string = """&savannah;/releases/acl/acl-&acl-version;.src.tar.gz"""
        query = ".*(\&[a-zA-Z0-9\-]*\;)+.*"
        match = regexp.match(query, string)

        # Iterate over the 'string' while matching
        while match:
            # Get the matched string. 'findall' returns a list
            found = regexp.findall(query, string)[0]
            # found = "&acl-version;"
            key = found.replace("&", "").replace(";", "")
            # key = "acl-version"
            placeholder = tools.generate_placeholder(key)
            # placeholder = "@@LFS_ACL_VERSION@@"
            # Finally, replace entity
            string = string.replace(found, placeholder)
            # Check if there is a new match
            match = regexp.match(query, string)

        return string

    def generate_entities_data_dict(self, entities_files=None):
        """
        Parse entities files and generate a dictionary.
        """
        data_dict = {}
        # Do not concat lines by default
        add_line = False
        saved_line = None
        html_comments_regexp = r"<!--(.|\s|\n)*?-->"

        # Sanitize input
        if tools.is_empty_list(entities_files):
            entities_files = self.entities_filelist

        for entity_file in entities_files:
            file_text = tools.read_file(entity_file)

            # Remove HTML comments from file_text.
            # It makes parsing entities much easier
            file_text = regexp.sub(html_comments_regexp,
                                   "",
                                   file_text,
                                   flags=regexp.DOTALL)

            # Restart flag for every file
            add_line = False

            for line in file_text.split("\n"):
                # Concatenate lines?
                if add_line is True:
                    line = saved_line + line

                # Remove leading and trailing whitespaces in line if any
                line = line.rstrip()

                # Check if 'line' is an ENTITY description line
                if line.find("ENTITY") != -1:
                    line_fields = line.split("\"")

                    # Process ENTITY line if we have a complete line.
                    # That is, it ends with '>' character
                    if line_fields[-1] == ">":
                        # line_fields = ['<!ENTITY attr-size ', '336 KB', '>']
                        key = line_fields[0].split(" ")[1]
                        # Process entities in 'value' if any
                        value = self.process_entities(line_fields[1])
                        # Add to dictionary
                        tools.add_to_dictionary(data_dict, key,
                                                value, concat=False)
                        # Restart flag. We begin with a new different line
                        add_line = False
                        saved_line = ""
                    else:
                        # Add next line to the new one and try to process it
                        saved_line = line
                        add_line = True

        # Return generated dictionary
        return data_dict

    def generate_components_filelist_from_index(self, indexfile, exclude=None):
        """
        Generate a list of components present in 'indexfile',
        usually the chapter's index file.
        """
        components_filelist = []
        directory = os.path.dirname(indexfile)
        # Get component list from chapter index
        file_text = tools.read_file(indexfile)

        for line in file_text.split("\n"):
            # Valid lines includes text 'xi:include' and are not XML comments
            if line.find("xi:include") != -1 and line.find("<!--") == -1:
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
                if(add is True and tools.is_empty_list(exclude) is False):
                    for e in exclude:
                        # Do not add it if match
                        if component.find(e) != -1:
                            add = False

                # Add it
                if add is True:
                    # Include absolute path
                    components_filelist.append(os.path.join(directory, component))

        return components_filelist

    def modify_xmlfile(self, component_recipe_data, componentfile_path):
        """
        Modify 'componentfile_path' XML file with common substitution and/or those
        in the 'component_substitution_list' entry of the component YAML recipe.

        This method can be overwritten in the 'functions.py' file under the component
        recipe directory. If so, arguments are:
            - 'component_recipe_data': current component data, which can be accessed and modified.
            - 'componentfile_path': XML file path in which you should do modifications.
            - 'parent_function': parent method reference.
        """
        # Remove 'literal' subchild so commands waiting the EOF string get properly parsed
        substitution_list = ["<literal>", "",
                             "</literal>", ""]

        #  Remove commands that try to run a bash console interactively
        bash_removes = ["exec /bin/bash --login +h",
                        "exec /tools/bin/bash --login +h",
                        """chroot $LFS /tools/bin/env -i            \
HOME=/root TERM=$TERM PS1='\u:\w\$ ' \
PATH=/bin:/usr/bin:/sbin:/usr/sbin   \
/tools/bin/bash --login""",
                        "chroot $LFS /tools/bin/env -i"]

        # Disable bash commands and add them to the 'substitution_list'
        bash_removes_disabled = tools.disable_commands(bash_removes)
        substitution_list.extend(bash_removes_disabled)

        # Get component data and include its 'substitution_list' and 'disable_commands'
        # elements into the 'substitution_list'
        if "component_substitution_list" in component_recipe_data and \
           component_recipe_data["component_substitution_list"] is not None:
            self.process_component_substitution_list(
                component_recipe_data["component_substitution_list"]
            )

            substitution_list.extend(component_recipe_data["component_substitution_list"])

        if "disable_commands_list" in component_recipe_data and \
           component_recipe_data["disable_commands_list"] is not None:
            substitution_list.extend(
                tools.disable_commands(
                    component_recipe_data["disable_commands_list"]
                )
            )

        if "comment_out_list" in component_recipe_data and \
           component_recipe_data["comment_out_list"] is not None:
            substitution_list.extend(
                tools.comment_out(
                    component_recipe_data["comment_out_list"]
                )
            )

        # Substitute
        tools.substitute_multiple_in_file(componentfile_path, substitution_list)

    def process_component_substitution_list(self, substitution_list):
        """
        Process 'component_substitution_list' data to convert
        'config.X_Y_Z' string to its 'config.py' file values
        """
        index = 0
        attribute = None
        for element in substitution_list:
            if element.startswith("config.") is True:
                attribute = element.split(".")[1]
                attribute = getattr(config, attribute)
                substitution_list[index] = attribute

            # Update index
            index += 1

    def generate_components_dict(self, components_filelist):
        """
        Generate 'components_dict' from 'components_filelist'.
        Parse component XML file.
        """
        components_dict = {}

        for componentfile_path in components_filelist:
            component_filename = os.path.basename(componentfile_path)

            component_name = self.get_component_name(component_filename)

            component_recipe_data = tools.read_recipe_file(component_name)

            # Backup xmlfile
            tools.backup_file(componentfile_path)

            # Read 'functions.py' file if exists
            self.extra_functions = tools.read_functions_file(component_name)

            # .- modify_xml
            if self.extra_functions is not None and \
               hasattr(self.extra_functions, "modify_xmlfile"):
                self.extra_functions.modify_xmlfile(component_recipe_data,
                                                    componentfile_path,
                                                    self.modify_xmlfile)
            else:
                self.modify_xmlfile(component_recipe_data, componentfile_path)

            # Create XML parser on every iteration
            parser = ET.XMLParser()
            parser.parser.UseForeignDTD(True)
            parser.entity = ShowAllEntities()
            etree = ET.ElementTree()
            xml_tree = etree.parse(componentfile_path, parser=parser)

            # Save components list to file
            tools.add_text_to_file(self.save_index_file, component_name)

            # Do not create build directory by default
            key = "{c}-require_build_dir".format(c=component_name)
            tools.add_to_dictionary(components_dict, key, "0")

            # Check 'screen/userinput' nodes
            for node in xml_tree.iter('screen'):
                if node.attrib.get('revision') == config.EXCLUDED_BOOT_MANAGER:
                    # skip unselected boot manager
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
                            key = component_name + "-require_build_dir"
                            tools.add_to_dictionary(components_dict,
                                                    key,
                                                    "1",
                                                    concat=False)
                            continue

                        # Skip patch calls as we do this step later on
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
                    elif attribute == "lfsbuilder_disabled":
                        # Do not run the "lfsbuilder_disabled" commands because
                        # it is not necessary
                        continue
                    else:
                        # By default, add it to the post steps.
                        # Stripping does not have 'remap' attribute
                        key = component_name + "-post"

                    # Add the value to dictionary
                    tools.add_to_dictionary(components_dict,
                                            key,
                                            subnode.text)

            # 'parser' is no longer required
            del parser

            # Restore backup
            if config.RESTORE_XML_BACKUPS is True:
                tools.restore_backup_file(componentfile_path)

        # Return generated dictionary
        return components_dict

    def write_commands_xmlfile(self, components_filelist, data_dict, filename):
        """
        Write 'builder_data.xml' file into the 'tmp' directory.
        Write XML file like:
         <components>
          <component name="">
           <version>1.0</version>
           <build_dir>0</build_dir>
           ...
          </component>
         </components>
        """

        # We will substitute 'data_dict' values twice to ensure composed placeholders
        # get substituted.
        substitution_rounds = 2

        # Create new XML tree
        root = ET.Element("components")
        for component_filepath in components_filelist:
            component_name = self.get_component_name(os.path.basename(component_filepath))
            c = ET.SubElement(root, "component", name=component_name)

            for attribute in self.xml_attributes_list:
                key = "{name}-{attribute}".format(name=component_name,
                                                  attribute=attribute)

                if key in data_dict:
                    ET.SubElement(c, attribute).text = data_dict[key]
                else:
                    ET.SubElement(c, attribute)

        # Write result
        filename = os.path.abspath(os.path.join(self.temporal_folder, filename))
        tools.write_xmlfile(filename, ET.tostring(root))

        # Substitute placeholders. Run substitutions twice because
        # some placeholders are composed
        i = 0
        while i < substitution_rounds:
            for key in data_dict:
                if data_dict[key] is not None:
                    placeholder = tools.generate_placeholder(key)
                    tools.substitute_in_file(filename, placeholder,
                                             data_dict[key])
            # Update loop index
            i += 1

    def parse_lfs_book(self, data_dict):
        """
        Steps to parse 'lfs' book's XML files.
        """
        components_filelist = []
        chapters_list = self.builder_data_dict["chapters_list"]
        exclude = self.builder_data_dict["excludes"]

        # Get data from every chapter
        for chapter in chapters_list:
            index_filename = "{c}.xml".format(c=chapter)
            index_path = os.path.abspath(os.path.join(self.book_basedir,
                                                      chapter, index_filename))

            # Get components list
            aux_components_filelist = self.generate_components_filelist_from_index(index_path,
                                                                                   exclude)

            components_filelist.extend(aux_components_filelist)

            # Get data from components list
            components_data_dict = self.generate_components_dict(aux_components_filelist)

            # Add obtained data to the 'data_dict'
            data_dict.update(components_data_dict)

        return components_filelist

    def modify_blfs_xmlfile(self, filepath_list):
        """
        Modify 'blfs' book's XML files attributes to be the same than 'lfs' book's.
        """
        substitution_list = ["-download-http", "-url",
                             "-md5sum", "-md5",
                             "<!--", "\n<!--"]

        for filepath in filepath_list:
            # Backup original file
            tools.backup_file(filepath)
            # Substitute values
            tools.substitute_multiple_in_file(filepath, substitution_list)

    def parse_blfs_book(self, data_dict):
        """
        Steps to parse 'blfs' book's XML files.
        """
        for component in self.builder_data_dict["components_to_build"]:
            filename = "{c}.xml".format(c=component)
            xmlfile_path = tools.find_file_recursive(self.book_basedir, filename)
            # Modify common values in BLFS XML files
            self.modify_blfs_xmlfile(xmlfile_path)
            # Add commands
            data_dict.update(self.generate_components_dict(xmlfile_path))

        return self.builder_data_dict["components_to_build"]

    def generate_commands_xmlfile(self):
        """
        Steps to generate XML commands file for builder.
        """
        components_filelist = []
        # Get general data from '.ent' files
        data_dict = self.generate_entities_data_dict()

        # Remove 'self.save_index_file' to avoid building components multiple times
        if os.path.exists(self.save_index_file):
            os.remove(self.save_index_file)

        # Parse LFS or BLFS book
        if self.builder_data_dict["book"] == "lfs":
            components_filelist = self.parse_lfs_book(data_dict)

        elif self.builder_data_dict["book"] == "blfs":
            components_filelist = self.parse_blfs_book(data_dict)
        else:
            msg = "Book '{b}' no to be parsed". format(b=self.builder_data_dict["book"])
            printer.warning(msg)

        # Get destination filename
        attribute = "{s}_XML_FILENAME".format(s=self.builder_data_dict["name"].upper())
        destination_filename = getattr(config, attribute)

        # Write XML file
        self.write_commands_xmlfile(components_filelist, data_dict, destination_filename)

    def generate_dict_from_xmlfile(self, filename):
        """
        Read XML command file and parse it into a Python dictionary.
        """
        data_dict = {}
        parser = ET.XMLParser()
        parser.parser.UseForeignDTD(True)
        parser.entity = ShowAllEntities()
        etree = ET.ElementTree()
        # Read commands from 'temporal_folder'
        filename = os.path.abspath(os.path.join(self.temporal_folder, filename))
        xml_tree = etree.parse(filename, parser=parser)

        # Iterate over 'component' nodes to extract data
        for node in xml_tree.iter('component'):
            component_name = node.attrib.get('name')
            for subnode in node:
                attribute = "{c}_{stag}".format(c=component_name,
                                                stag=subnode.tag)
                # Add to dictionary
                tools.add_to_dictionary(data_dict, attribute,
                                        subnode.text, concat=False)
        # return generated dictionary
        return data_dict
