# Configuration

The file `config.py` is the main configuration file for the LFSBuilder tool. It allows you to configure the behaviour of the LFSBuilder tool. Several of the configuration parameters are present as command line arguments.

You can check if the `config.py` file is correct by running a

You can find below a list of the available options with a brief description of them.


* **BASE\_DIRECTORY**: base directory to build the Linux from Scratch system.
* **NON\_PRIVILEGED\_USERNAME**: name of the unprivileged user that will build `toolchain` components. It is also used to create a new user in the final system if you build the Beyond Linux from Scratch's `createuser` component.
* **LFS\_VERSION**: version of the book to build.
* **MOUNT\_SOURCES\_DIRECTORY**: whether you want to mount the `sources` directory into the chroot or not.
* **SOURCES\_ORIG\_DIRECTORY**: path to the `sources` directory to be mount into the chroot. You can use a relative path to the LFSBuilder source code directory using the special string`@@LFSBUILDER\_SRC\_DIRECTORY@@`.
* **MAKEFLAGS**: defines the `MAKEFLAGS` environment variable to define `make` options.
* **ROOT\_PASSWD**: password for the `root` user in the final system.
* **NON\_PRIVILEGED\_USERNAME\_PASSWD**: password of the `NON\_PRIVILEGED\_USERNAME` in the final system created with the `createuser` component.
* **GENERATE\_DATA\_FILES**: indicates if the XML parser has to generate the builder's XML files or not. Boolean parameter.
> <div class="warning-quote"> NOTE: the build process will fail if these files don't exist.
* **RESTORE\_XML\_BACKUPS**: restore or not original XML files after the parse process. Boolean parameter.
* **GENERATE\_IMG\_FILE**: generate or not a `.img` file to build the final system on it or not. Boolean parameter.
* **MOUNT\_IMG\_FILE**: mount or not the `.img` file. Boolean parameter.
* **IMG\_FILENAME**: path to the `.img` file that will be mounted as `BASE\_DIRECTORY`. You can use a relative path to the LFSBuilder source code directory using the special string`@@LFSBUILDER\_SRC\_DIRECTORY@@`.
* **IMG\_SIZE**: size of the `.img` file. A value of around 10 gigabytes is recommended. Units: `M` for megabytes and `G` for gigabytes.
* **CUSTOM\_COMPONENTS\_TO\_BUILD**: choose if components from the Linux from Scratch book are built in the book's order or not. The customized order is defined by the `components\_to\_build` property of the builder YAML file. Boolean parameter.
* **SYSV**: use the SysVinit init system. Boolean parameter.
* **SYSTEMD**: use the Systemd init system. Boolean parameter.
* **INCLUDE\_MESON\_BUILDER**: from Linux from Scratch 8.2, it is mandatory to build the `python`, `ninja` and `meson` components when using Systemd. The tool will fail if this option is not set. Boolean parameter.
* **SAVE\_TOOLCHAIN**: choose if the toolchain created will be saved as a `.tar.gz` file or not. Boolean parameter.
* **SAVE\_TOOLCHAIN\_FILENAME**: name for the `.tar.gz` file containing the toolchain. If the value is of the form `lfsbuilder-toolchain-@@LFS\_VERSION@@`, then the compressed file name is:
```
lfsbuilder-toolchain-${lfs_version}-${date}.tar.gz}
```
* **DELETE\_TOOLS**: to delete or not the `/tool` directory after building the `system` builder. Boolean parameter.
* **TIMEZONE**: timezone to set in the final system. You can use the `tzselect` command to choose the one of your preference.
* **PAPER\_SIZE**: value to configure the `groff` component. Values are: `letter` and `A4`.
* **KEYMAP**: keyboard language.
* **CONSOLE\_FONT**: system console font.
* **LANG**: language of the final system. Using `UTF-8` encoding is recommended.
* **LOCALE**: value for the rest of the language configuration variables.
* **CHARMAP**: default encoding for the system characters. Using `UTF-8` encoding is recommended.
* **ROOT\_PARTITION\_NAME**: name of the disk device containing the root partition of the final system. It configures some `grub` options.
* **ROOT\_PARTITION\_NUMBER**: partition number of the root system partition. Used for configuring `grub`.
* **GRUB\_ROOT\_PARTITION\_NAME**: name of the device to install `grub`.
* **GRUB\_ROOT\_PARTITION\_NUMBER**: disk device name and partition number in which `grub` will look for the `kernel` to boot.
* **FILESYSTEM\_PARTITION\_TYPE**: filesystem type of the disk in which the final system will be installed.
* **SWAP\_PARTITION\_NAME**: name and number of the swap partition that will be set in the `/etc/fstab` file.
* **ETH0\_IP\_ADDRESS**: IP address for the `eth0` network interface.
* **ETH0\_GATEWAY\_ADDRESS**: IP address of the gateway for the `eth0` network interface.

TODO

* **ETH0\_BROADCAST\_ADDRESS**: Dirección IP de difusión para la interfaz de red \textconsole{eth0}.
* **ETH0\_MASK**: Máscara de red para la interfaz \textconsole{eth0}.
* **DOMAIN\_NAME**: Nombre de dominio a utilizar para la configuración de red.
* **DNS\_ADDRESS\_1**:
* **DNS\_ADDRESS\_2**: Direcciones IP usadas por el protocolo de descubrimiento dinámico de dominios de red \textit{DNS}.
* **HOSTNAME**: Nombre del equipo del sistema operativo construido.
* **DISTRIBUTION\_NAME**: Nombre de la distribución construida.
* **DISTRIBUTION\_VERSION**: Versión de la distribución construida.
* **DISTRIBUTION\_DESCRIPTION**: Descripción de la distribución construida.
* **REMOVE\_REBOOT\_COMPONENT**: Opción binaria. Este parámetro desactiva la ejecución del componente \componente{reboot} del libro \textit{Linux from Scratch}. Su valor debe ser siempre \textconsole{True} porque el constructor \textconsole{collector} realiza su función de forma más adecuada.
* **MOUNT\_SYSTEM\_BUILDER\_DIRECTORIES**: Opción binaria que decide si los directorios del sistema deben montarse en el directorio base de construcción antes de iniciar el proceso o no.
* **VERBOSE**: Opción binaria que muestra mayor cantidad de información al usuario.
* **DEBUG\_SCRIPTS**: Muestra los comandos que componen un \textit{script} a medida que se ejecutan. Opción binaria.
* **CONTINUE\_AT**: Esta opción permite iniciar la construcción de un determinado constructor por un determinado componente. Sólo es válido para los constructores \textconsole{toolchain}, \textconsole{system}, \textconsole{configuration} y \textconsole{blfs}.
