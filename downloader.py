
import os
import sys
import urllib2

import config
import tools
import printer

class Downloader(object):
    def __init__(self, name):
        self.downloader_data = {
            "name": name,
            "lfs_svn_command": "svn co svn://svn.linuxfromscratch.org/LFS/tags/{v}/ lfs".format(
                v = config.LFS_VERSION),
            "blfs_svn_command": "svn co svn://svn.linuxfromscratch.org/BLFS/tags/{v}/ blfs".format(
                v = config.LFS_VERSION),
            "lfs_wget_link": "http://www.linuxfromscratch.org/lfs/view/{v}/wget-list".format(
                v = config.LFS_VERSION),
            "lfsbuilder_src_directory": os.path.dirname(os.path.realpath(__file__)),
            "lfsbuilder_tmp_directory": os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                     "tmp"),
            "lfsbuilder_sources_directory": os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                         "tmp", "sources"),

            "download_wgetlist_command": "wget --input-file=wget-list --continue --directory-prefix={s}"

            }

    def download_xml(self):
        printer.info("About to download XML files for '{n}'".format(n=self.downloader_data["name"]))
        os.chdir(self.downloader_data["lfsbuilder_tmp_directory"])
        cmd_name = "{n}_svn_command".format(n=self.downloader_data["name"])
        cmd = self.downloader_data[cmd_name].format(v=config.LFS_VERSION)

        tools.run_program_with_output(cmd)

    def download_source(self):

        if self.downloader_data["name"] == "blfs":
            printer.error("Downloading sources for 'blfs' is not currently available")

        printer.info("About to download source code for '{n}'".format(n=self.downloader_data["name"]))
        tools.create_directory(self.downloader_data["lfsbuilder_sources_directory"])

        os.chdir(self.downloader_data["lfsbuilder_sources_directory"])

        # Download the 'wget-list' file
        printer.info("Downloading 'wget-list' for '{n}'".format(n=self.downloader_data["name"]))
        wget_list_filename = self.downloader_data["lfs_wget_link"].split("/")[-1]
        self.download_file_from_url(wget_list_filename, self.downloader_data["lfs_wget_link"])

        # Download sources from 'wget-list'
        printer.info("Downloading sources for '{n}'".format(n=self.downloader_data["name"]))
        for url in tools.list_from_file(wget_list_filename):
            filename = url.split("/")[-1]
            self.download_file_from_url(filename, url)

    def download_file_from_url(self, filename, url):
        msg = "Downloading file '{f}' from '{u}'".format(f = filename,
                                                         u = url)
        printer.substepInfo(msg)
        # .- open socket
        url_socket = urllib2.urlopen(url)
        # .- read from socket
        tools.write_file(filename, url_socket.read())
        # .- close socket
        url_socket.close()
