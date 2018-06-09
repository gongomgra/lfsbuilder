
import os
import datetime

import tools
import config

def run_post_steps(component_data_dict, parent_function):

    # Compress 'config.BASE_DIRECTORY/tools' directory to
    # 'config.SAVE_TOOLCHAIN_FILENAME-ddmmyyyy.tar.gz' if
    # 'config.SAVE_TOOLCHAIN' is True
    if config.SAVE_TOOLCHAIN is True:
        date = datetime.date.today().strftime("%d%m%Y")
        filename = "{f}-{d}.tar.gz".format(
            f=config.SAVE_TOOLCHAIN_FILENAME,
            d=date
        )

        output_filename_path = os.path.abspath(
            os.path.join(
                component_data_dict["lfsbuilder_tmp_directory"],
                filename
            )
        )

        # Remove existent tarball
        if os.path.exists(output_filename_path):
            os.remove(output_filename_path)

        # Add 'backup_tools_cmd' to 'post'
        cmd = component_data_dict["backup_tools_cmd"]
        cmd = cmd.format(df=output_filename_path)

        # book's 'changingowner' commands change directory owner/group to
        # 'root' user. We will back 'tools' directory up before.
        cmd = """{cmd}
{post}""".format(cmd=cmd, post=component_data_dict["post"])

        tools.add_to_dictionary(
            component_data_dict,
            "post",
            cmd,
            concat=False
        )

    # Run parent function
    parent_function()
