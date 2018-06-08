"""
downloader.py

Download logic for both 'lfs' and 'blfs' books.
"""
import os
import urllib2
import shutil

import config
import tools
import xmlparser
import builders
import printer


class Downloader(object):
    """
    Downloader class.

    Implements logic for downloading XML and source tarballs required to build
    both 'lfs' and 'blfs' books.
    """
    def __init__(self, name):
        self.downloader_data = {
            "name": name,
            "lfs_svn_command": "svn co svn://svn.linuxfromscratch.org/LFS/tags/{v}/ lfs".format(
                v=config.LFS_VERSION),
            "blfs_svn_command": "svn co svn://svn.linuxfromscratch.org/BLFS/tags/{v}/ blfs".format(
                v=config.LFS_VERSION),
            "lfs_wget_link": "http://www.linuxfromscratch.org/lfs/view/{v}/wget-list".format(
                v=config.LFS_VERSION),
            "lfsbuilder_src_directory": os.path.dirname(os.path.realpath(__file__)),
            "lfsbuilder_tmp_directory": os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                     "tmp"),
            "lfsbuilder_sources_directory": os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "tmp", "sources")

        }
        self.lfs_builders = ["toolchain", "system", "configuration"]
        self.blfs_builders = ["blfs"]

    def download_xml(self):
        """
        Download XML files for the provided book 'name' under the 'tmp' directory.
        """
        msg = "Download XML files for '{n}'"
        msg = msg.format(n=self.downloader_data["name"])
        printer.info(msg)

        os.chdir(self.downloader_data["lfsbuilder_tmp_directory"])

        # Delete destination folder if exists
        if os.path.exists(self.downloader_data["name"]) is True:
            # Delete directory to download new files
            shutil.rmtree(self.downloader_data["name"])

        cmd_name = "{n}_svn_command".format(n=self.downloader_data["name"])
        cmd = self.downloader_data[cmd_name].format(v=config.LFS_VERSION)

        if config.VERBOSE is True:
            tools.run_program_with_output(cmd)
        else:
            tools.run_program_without_output(cmd)

    def download_source(self):
        """
        Download source code files.
        """
        msg = "Download source code for '{n}'"
        msg = msg.format(n=self.downloader_data["name"])
        printer.info(msg)

        # Create 'sources' directory
        tools.create_directory(self.downloader_data["lfsbuilder_sources_directory"])

        # Download for selected builder
        if self.downloader_data["name"] == "lfs":
            self.download_lfs_sources()
        elif self.downloader_data["name"] == "blfs":
            self.download_blfs_sources()
        else:
            msg = "Downloading sources for '{b}' is not currently available"
            msg = msg.format(b=self.downloader_data["name"])
            printer.error(msg)

    def download_lfs_sources(self):
        """
        Download sources for 'lfs'.
        """
        urls_list = []

        # .- get 'urls' from 'extra_download_urls' for
        # components on 'lfs' book's builders
        urls_list = self.get_download_urls()

        # .- move into 'sources' directory
        os.chdir(self.downloader_data["lfsbuilder_sources_directory"])

        # .- download the 'wget-list' file
        printer.info("Downloading 'wget-list' for '{n}'".format(n=self.downloader_data["name"]))
        wget_list_filename = self.downloader_data["lfs_wget_link"].split("/")[-1]
        self.download_file_from_url(wget_list_filename, self.downloader_data["lfs_wget_link"])

        # .- add download urls from 'wget-list'
        for url in tools.list_from_file(wget_list_filename):
            if (url is not None) and (url not in urls_list):
                urls_list.append(url)

        printer.info("Downloading sources for '{n}'".format(n=self.downloader_data["name"]))

        # .- ensure there is no any empty string on 'urls_list'
        tools.remove_element(urls_list, "")

        # .- download
        for url in urls_list:
            if url is not None:
                filename = url.split("/")[-1]
                self.download_file_from_url(filename, url)

    def download_blfs_sources(self):
        """
        Download sources for 'blfs'.
        """
        urls_list = []

        # .- get 'urls' from 'extra_download_urls' for
        # components on 'lfs' book's builders
        urls_list = self.get_download_urls()

        # .- move into 'sources' directory
        os.chdir(self.downloader_data["lfsbuilder_sources_directory"])

        # .- ensure there is no any empty string in 'urls_list'
        tools.remove_element(urls_list, "")

        # .- download
        for url in urls_list:
            if url is not None:
                filename = url.split("/")[-1]
                self.download_file_from_url(filename, url)

    def download_file_from_url(self, filename, url):
        """
        Download file 'filename' from the provided 'url'.
        """
        msg = "Downloading file '{f}' from '{u}'".format(f=filename,
                                                         u=url)
        printer.substep_info(msg)

        # .- open socket
        url_socket = urllib2.urlopen(url)
        # .- read from socket
        tools.write_file(filename, url_socket.read())
        # .- close socket
        url_socket.close()

    def get_download_urls(self):
        """
        Generate list with 'extra_download_urls' values for components
        on lfs book.
        """
        urls_list = []
        aux_urls_list = []

        # We will substitute entities values twice to ensure composed placeholders
        # get substituted
        substitution_rounds = 2

        builders_list = self.lfs_builders
        if self.downloader_data["name"] == "blfs":
            builders_list = self.blfs_builders

        # .- generate builders in 'lfs' book, get 'components_to_build'
        # list and add 'extra_download_urls' from components recipes.
        for builder in builders_list:
            os.chdir(self.downloader_data["lfsbuilder_src_directory"])
            # .- generate builder object from BuilderGenerator
            bg = builders.BuilderGenerator(builder)
            b = bg.get_builder_reference()
            del bg

            # .- read entities in case we need to substitue in any URL
            xmlp = xmlparser.LFSXmlParser(
                b.builder_data_dict
            )

            # .- write commands xml file and read it
            xmlp.generate_commands_xmlfile()
            destination_filename = getattr(
                config,
                "{b}_XML_FILENAME".format(
                    b=b.builder_data_dict["name"].upper()
                )
            )
            components_data_dict = xmlp.generate_dict_from_xmlfile(destination_filename)

            # .- read entities so we can do substitutions in case it is necessary
            entities_data = xmlp.generate_entities_data_dict()

            # .- always download 'blfs-bootscripts' component for 'blfs',
            # which includes both 'blfs-bootscripts' for 'sysvinit' and
            # 'blfs-systemd-units' for 'systemd' tarballs
            # to be able to install services at build time.
            if self.downloader_data["name"] == "blfs":
                tools.remove_all_and_add_element(
                    b.builder_data_dict["components_to_build"],
                    "blfs-bootscripts"
                )

            # .- add 'extra_download_urls' from builder 'components_to_build' recipes.
            if b.builder_data_dict["components_to_build"] is not None:
                for component in b.builder_data_dict["components_to_build"]:
                    # .- read component recipe
                    component_recipe_data = tools.read_recipe_file(component)

                    # .- add 'extra_download_urls' if present in 'component_recipe_data'
                    if "extra_download_urls" in component_recipe_data and \
                       component_recipe_data["extra_download_urls"] is not None:
                        # add to 'aux_urls_list' if not present already
                        for url in component_recipe_data["extra_download_urls"]:
                            # .- process_entities in url
                            url = xmlp.process_entities(url)
                            if url not in aux_urls_list:
                                # .- substitute entities
                                i = 0
                                while i < substitution_rounds:
                                    for entity_key in entities_data.keys():
                                        url = url.replace(
                                            tools.generate_placeholder(entity_key),
                                            entities_data[entity_key]
                                        )
                                    # .- update index
                                    i += 1

                                # .- add 'url' to 'aux_urls_list'
                                aux_urls_list.append(url)

                    # .- update 'component_url' in case it is present in 'component_recipe_data'
                    key = "{c}_url".format(c=component)
                    if key in component_recipe_data and component_recipe_data[key] is not None:
                        # .- update value read 'components_data'
                        tools.add_to_dictionary(
                            components_data_dict,
                            key,
                            component_recipe_data[key],
                            concat=False
                        )

                    # .- add 'component_url' to the 'aux_urls_list'
                    if components_data_dict[key] is not None and \
                       components_data_dict[key] not in aux_urls_list:
                        # .- substitute entities
                        url = components_data_dict[key]
                        # .- process_entities in url
                        url = xmlp.process_entities(url)
                        i = 1
                        while i < substitution_rounds:
                            for entity_key in entities_data.keys():
                                url = url.replace(
                                    tools.generate_placeholder(entity_key),
                                    entities_data[entity_key]
                                )
                            # .- update index
                            i += 1

                        # .- add to 'aux_urls_list'
                        aux_urls_list.append(url)

            # .- delete 'builder' reference
            del b

        for url in aux_urls_list:
            # .- add modified url. Check is not present in
            # 'urls_list' in case there are duplicated componentes.
            # For example, 'binutils' and 'binutils2'
            if (url is not None) and (url not in urls_list):
                urls_list.append(url)

        # .- return generated 'urls_list' and
        # ensure there is no any empty string on it
        tools.remove_element(urls_list, "")
        return urls_list
