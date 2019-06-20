# Usage

LFSBuilder requires Python 3.x to be run. The Python 2.x versions support has been dropped as its [end of life date](https://www.python.org/dev/peps/pep-0373/#update) is just around the corner. Once the required dependencies are installed you can start using it.

The main configuration file is the `config.py` file located in the main directory of the program. In this file you customize the behaviour of the program, such as where will the chroot be located, which version of Linux from Scratch you want to build, and others. Some of those options have an equivalent command line option that will overwrite the value of the parameter in that config file. If you are not familiar with the Linux/UNIX command line and the source code compilation process, it is recommended to use the default values in the file.

From now on, this text will suppose that you have satisffied the requirements of both projects, Linux from Scratch and LFSBuilder, and also has a correct `config.py` file. You can run the next unit test to check it:

```
python3 -B -m unittest -f tests/test_config.py
```

The help message of the LFSBuilder command line interface is shown below for further reference:

```
$ python3 -B lfsbuilder.py --help
usage: lfsbuilder.py [-h] [-v] [--debug-scripts]
                     [--base-directory BASE_DIRECTORY]
                     [--non-privileged-username NON_PRIVILEGED_USERNAME]
                     [--sources-orig-directory SOURCES_ORIG_DIRECTORY]
                     [--makeflags MAKEFLAGS]
                     [--restore-xml-backups RESTORE_XML_BACKUPS]
                     [--lfs-version LFS_VERSION]
                     ...

positional arguments:
  {build,download,parse}
                        Subcommand to run

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Output verbose messages
  --debug-scripts       Debug scripts when running
  --base-directory BASE_DIRECTORY
                        Set base directory
  --non-privileged-username NON_PRIVILEGED_USERNAME
                        Set non privileged username
  --sources-orig-directory SOURCES_ORIG_DIRECTORY
                        Set origin directory for sources
  --makeflags MAKEFLAGS
                        Set MAKEFLAGS value
  --restore-xml-backups RESTORE_XML_BACKUPS
                        Restore XML backups files
  --lfs-version LFS_VERSION
                        Version of the book

```

The main actions you can do with LFSBuilder are explained next:

* _Download_ books' source files and source code.
* _Parse_ book's XML files.
* _Build_ one or multiple builders.

### Downloading books source files and components source code

The LFSBuilder tool can download the XML files for the Linux from Scratch and Beyond Linux from Scratch versions that will be build. To do so, use the `download` command with the `lfsbuilder.py` main script from the LFSBuilder main directory. For example. to download the XML files for the Linux from Scratch book, you run


```
python3 -B lfsbuilder.py download --xml lfs
```

The command above will download the LFS book for the version set in the `LFS_VERSION` parameter of the `config.py` file. If you want to download a different version than the one in the config file, you can use the `--lfs-version` command line parameter that overwrites the mentioned parameter at run time:

```
python3 -B lfsbuilder.py --lfs-version 7.9 download --xml lfs
```

You can check the downloaded version under the `/tmp/lfs/general.ent` file running the command below

```
grep "ENTITY version" ./tmp/lfs/general.ent
```

Downloading the source code for a book's list of components is also possible. To do that, you need to specify the `--source` selector to the `download` command instead of `--xml`:

```
python3 -B lfsbuilder.py download --source blfs
```

> <div class="warning-quote"> NOTE: it is required to download book's XML files before downloading the source code packages. </div>

You may find issues trying to download sources for the BLFS book. This is a known issue and will be fixed in a future release. Please manually download packages in that case.

### Parsing XML files

For both books, the Linux from Scratch and Beyond Linux from Scratch, the LFSBuilder tool parses the XML files into a single XML file with all the metadata and required commands to build each component. With that, LFSBuilder concentrate all the information for each step (that is, from one or more book chapters), into one single file. The result XML file is later imported into LFSBuilder to build the required components.

To parse a single builder of the Linux from Scratch book (either `toolchain`, `system` or `configuration`), the next command should be executed into the main LFSBuilder directory:

```
python3 -B lfsbuilder.py parse toolchain
```

> **NOTE**: The command above can receive a space-separated list of builders to parse

It is also possible to parse all the three parts of the Linux From Scratch book without specifying them but using the special name `lfs`. This alias also works for the build step.

```
python3 -B lfsbuilder.py parse lfs
```

### Building

The build command is aim to build the different components that are part of a specific builder. This command is required to be run as the **root** user (use `sudo` to achieve that from a regular user) as it requires access to privileged commands in your system such as `mount`, `chroot`, `mkfs` and others.

The LFSBuilder utility runs the build process inside a chrooted directory, so it is isolated from the rest of the system. Also, by default it creates a `.img` file into the `tmp` directory inside the LFSBuilder main folder that is then mounted on your system. Once the build process has finished, you can convert the `.img` file to the [VMDK virtual machine format](https://en.wikipedia.org/wiki/VMDK) or any other virtual machine format so you can test your new system.

To build the Linux from Scratch book, it is necessary to run a command similar to this:

```
sudo python3 -B lfsbuilder.py build lfs
```

You can add many arguments to the command above that will tune the build. You can set the base directory, the init system (`sysv` or `systemd`), and others. These options have higher preferences than the values in the `config.py` file. The latest argument of the build command is an ordered list of builders. This list will be checked and modify according to the next points:

* Duplicates builders are forbidden.
* The `provider` and `collector` builders will be added automatically at the beginning and the end of the list respectively. Those special builders take care of prepare and clean the build environment.
* The Linux from Scratch book's builders must be built on its prefixed order: `toolchain`, `system` and `configuration`. You can run them in a different order if you only build one builder at a time, but **you are highly advised to not to do it**.
* You can include your own builders in any position as long as you keep the order:
    * `toolchain` must be the first of the three of them.
    * `system` must be built before `configuration`.

With all the previous information, the next command will run a build that generates a `.img` file, mounts it in your system, will mount the required system directories into the chroot and the downloaded sources files as well for the build process to be able to find them. It will also build the `systemd` version of the Linux from Scratch and the Beyond Linux from Scratch books and another different custom builder called `mybuilder`.

```
sudo python3 -B lfsbuilder.py build \
    --generate-img-file --mount-img-file \
    --mount-system-directories --mount-sources \
    --systemd lfs blfs mybuilder
```

In case you find any issue building one of the components of a builder, you can restart the build process from that component directly instead of building all the components of the builders using the special argument `--continue-at`. For example

```
sudo python3 -B lfsbuilder.py build \
    --no-generate-img-file --no-mount-img-file \
    --no-mount-system-directories --no-mount-sources \
    --continue-at=failed-component mybuilder
```

> **NOTE**: the `--continue-at` parameter will only work for a component present in the first builder of the given list.
