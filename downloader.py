"""
downloader.py

Download logic for both 'lfs' and 'blfs' books.
"""
import os
import urllib2
import shutil

import config
import tools
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
        msg = "About to download XML files for '{n}'"
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
        if self.downloader_data["name"] == "blfs":
            printer.error("Downloading sources for 'blfs' is not currently available")

        msg = "About to download source code for '{n}'"
        msg = msg.format(n=self.downloader_data["name"])
        printer.info(msg)

        tools.create_directory(self.downloader_data["lfsbuilder_sources_directory"])

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
