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
                "tmp", "sources"),

        }

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
        # Move into 'sources' directory
        os.chdir(self.downloader_data["lfsbuilder_sources_directory"])

        # Download the 'wget-list' file
        printer.info("Downloading 'wget-list' for '{n}'".format(n=self.downloader_data["name"]))
        wget_list_filename = self.downloader_data["lfs_wget_link"].split("/")[-1]
        self.download_file_from_url(wget_list_filename, self.downloader_data["lfs_wget_link"])

        # Download sources from 'wget-list'
        printer.info("Downloading sources for '{n}'".format(n=self.downloader_data["name"]))
        for url in tools.list_from_file(wget_list_filename):
            if url:
                filename = url.split("/")[-1]
                self.download_file_from_url(filename, url)

    def download_blfs_sources(self):
        """
        Download sources for 'blfs'.
        """
        urls_list = []

        # .- read 'blfs' command file to retrieve components url
        components_filename = getattr(config, "BLFS_XML_FILENAME")
        components_filepath = os.path.join(
            self.downloader_data["lfsbuilder_tmp_directory"],
            components_filename
        )

        # .- ask user to parse book in case the 'BLFS_XML_FILENAME'
        # do not exists
        if os.path.exists(components_filepath) is False:
            msg = """Downloading sources for 'blfs' book requires to parse book first.
         Please, run 'parse' command first."""
            printer.error(msg)

        xmlp = xmlparser.LFSXmlParser({"name": "blfs", "book": "blfs"})
        components_data = xmlp.generate_dict_from_xmlfile(components_filepath)

        # .- get builder recipe data to retrieve 'components_to_build' list
        builder_recipe_data = tools.read_recipe_file(
            self.downloader_data["name"],
            directory="builders"
        )

        # .- read entities in case we need to substitute in any URL
        entities_data = xmlp.generate_entities_data_dict()

        # .- always download 'blfs-bootscripts', which includes both
        # 'blfs-bootscripts' for 'sysvinit' and
        # 'blfs-systemd-units' for 'systemd' tarballs
        # to be able to install services at build time.
        tools.remove_all_and_add_element(
            builder_recipe_data["components_to_build"],
            "blfs-bootscripts"
        )

        # .- generate url list with the 'component-url' from 'components_data'
        # and the 'extra_download_urls' from every component recipe.
        for component in builder_recipe_data["components_to_build"]:
            # .- update 'components_data' with 'componet' recipe
            component_recipe_data = tools.read_recipe_file(component)
            components_data = tools.join_dicts(components_data, component_recipe_data)

            # .- retrieve 'component-url' value if present
            key = "{c}_url".format(c=component)
            if key in components_data and components_data[key] is not None:
                urls_list.append(components_data[key])

            # .- add 'extra_download_urls' if present in 'component_recipe_data'
            if "extra_download_urls" in component_recipe_data:
                urls_list.extend(component_recipe_data["extra_download_urls"])

        # Move into 'sources' directory
        os.chdir(self.downloader_data["lfsbuilder_sources_directory"])

        # .- download files in 'urls_list'
        for url in urls_list:
            # Try to subsitute entities on URL
            for key in entities_data.keys():
                url = url.replace(
                    tools.generate_placeholder(key),
                    entities_data[key]
                )
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
