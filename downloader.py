
import os
import sys

import config
import tools
import printer

class Downloader(object):
    def __init__(self, name):
        self.downloader_data = {
            "name": name,
            "lfs_svn_command": "svn co svn://svn.linuxfromscratch.org/LFS/tags/{v}/ lfs",
            "blfs_svn_command": "svn co svn://svn.linuxfromscratch.org/BLFS/tags/{v}/ blfs",
            "lfs_wget_link": "http://www.linuxfromscratch.org/lfs/view/{v}/wget-list",
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
            printer.warning("Downloading sources for 'blfs' is not currently available")
            sys.exit(1)

        printer.info("About to download source code for '{n}'".format(n=self.downloader_data["name"]))
        tools.create_directory(self.downloader_data["lfsbuilder_sources_directory"])

        os.chdir(self.downloader_data["lfsbuilder_sources_directory"])

        # Download the 'wget-list' file
        printer.info("Downloading 'wget-list' for '{n}'".format(n=self.downloader_data["name"]))
        cmd = "wget {l}".format(l = self.downloader_data["lfs_wget_link"]).format(v = config.LFS_VERSION)
        tools.run_program_with_output(cmd)

        # Download sources from 'wget-list'
        printer.info("Downloading sources for '{n}'".format(n=self.downloader_data["name"]))
        cmd = self.downloader_data["download_wgetlist_command"].format(
            s=self.downloader_data["lfsbuilder_sources_directory"])
        tools.run_program_with_output(cmd)
