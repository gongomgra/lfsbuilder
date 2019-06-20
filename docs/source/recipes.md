# Recipes

A _recipe_ defines one of the basic component types of the LFSBuilder tool: `builders` and `components`. It is composed by a directory and a file both named after the component name. Apart from that, you can include a `functions.py` optional file that modify the way some core functions work with the component, or your own extra functions. As an example, under the `recipes/builders/toolchain` directory you can find the `toolchain.yaml` and `functions.py` files.

Recipes represent a customizable extra layer on top of the core functions of the LFSBuilder tool that allows you to customize your final system without the need of modifying its code. It also isolates issues because if a component is broken due to a bad configuration or function definition, it will only affect that component.

## Properties
The `${component}.yaml` file is mandatory, and its minimum content is the `name` property. This attribute defines the value of several internal variables used by the LFSBuilder tool. You can also provide the `base_component` property to define the type of component you are defining. The options available for this property are:

* **SystemConfigurationComponent**: this component type only modifies the final system in some way (generating files, directories, setting permissions...) but is not _built_ using the compilation steps.
* **CompilableComponent**: this component is built using the `configure`/`make` tools.

You can also define your own properties. They will be available at build time in the `component_data_dict` dictionary.

#### Available properties

* **package\_name**: name of the source code tarball file.
* **previous**: steps to be performed before starting the build process. Patches are applied before this step, right after uncompressing the source code.
* **configure**: commands to configure the component. It replaces the configure commands from the book.
* **configure\_options**: extra options for the `configure` command. Added after books' provided options.
* **make**: command that build the component. Usually `make`.
* **make\_options**: extra options for the `make` command.
* **install**: command to run for installing the built libraries and binaries. Usually `make install`.
* **install\_options**: extra options for the previous command.
* **test**: commands to run instead of `make test` or `make check`.
* **test\_options**: extra options for the previous command.
* **include\_tests**: boolean parameter that enables/disables test execution.
* **post**: steps to be run after the build process.
* **env\_PATH\_value**: custom value for the `PATH` environment variable that will be used to build all the components that belong to a specific `builder`.
* **book**: the defined component belongs to that book. Valid values: `lfs`, `blfs` and `custom`.
* **run\_as\_username**: username that will build the component.
* **run\_into\_chroot**: whether a component should be build from inside the `chroot` or not.
* **version**: component version to build.
* **comment\_out\_list**: list of commands in the component's XML files that will be commented out.
* **components\_to\_build**: ordered list of components to build for a desired builder if the `CUSTOM\_COMPONENTS\_TO\_BUILD` property is true.
* **component\_substitution\_list**: sustitutions to be performed in the component's XML file.
* **chapters\_list**: list of book chapters that include each build step of the Linux from Scratch book: `toolchain`, `system` and `configuration`.
* **disable\_commands\_list**: commands that will be ignored by the `LFSXmlParser` class, and therefore won be run.
* **runscript\_cmd**: command used to run a compilation script.

## Functions

The `functions.py` file allows you to customize the way some core functions interact with a component. As an example. the `kernel` component overwrites the `run_previous_steps` core function to, apart from running the core logic, copy the kernel configuration file that will be used to compile it. The content of the `functions.py` file for the `kernel` component is:

```
import os
import sys

import config
import tools

def run_previous_steps(component_data_dict, parent_function):

    # Call parent function
    parent_function()

    print("Copying custom \'.config\' file")
    filename = os.path.join(component_data_dict["lfsbuilder_src_directory"],
                            "recipes",
                            "components",
                            "kernel",
                            "files",
                            component_data_dict["kernel_config_filename"])

    tools.copy_file(filename,
                    os.path.join(component_data_dict["extracted_directory"], ".config")
    )
```

As shown above, that component defines the `kernel_config_filename` custom property, which contains the name of the configuration file to be used. All the functions that can be overwritten always receive the same parameters:

* **component\_data\_dict**: a Python dictionary with the current values of the component metadata (name, version, commands to run...). You can modify these values from a custom function.
* **parent\_function**: references the core function that is being overwriten. From a _object oriented programming_ point of view, it allows you to run the `super` class function.

The list of the core functions that can be customized is present below

#### Available functions

* **apply\_patches**: looks and apply a source code patch.
* **build**: required steps to build components of a specific builder.
* **extract\_source\_code**: defines how a source code tarball is extracted.
* **get\_components\_to\_build\_list**: returns the list of components that a specific builder builds. This function can be used to modify that list, for example depending on the value of a configuration property.
* **modify\_xmlfile**: modifies a component or builder XML file before parsing it.
* **run\_post\_steps**: steps to run after a component is build and installed.
* **run\_previous\_steps**: steps run right after extracting the component source code and before starting the build process.
* **set\_attributes**: allows you to modify the component attributes before starting the build process.
