# Basic structure

The basic structure of the LFSBuilder tool is shown in the diagram below

```
lfsbuilder/
├── actions.py
├── builders.py
├── cli.py
├── components.py
├── config.py
├── downloader.py
├── lfsbuilder.py
├── printer.py
├── prueba.py
├── recipes/
│   ├── builders/
│   └── components/
├── requirements.txt
├── templates/
│   ├── script.tpl
│   └── setenv.tpl
├── tests/
│   ├── __init__.py
│   ├── test_actions.py
│   ├── test_config.py
│   ├── test_downloader.py
│   ├── test_tools.py
│   └── test_xmlparser.py
├── tools.py
└── xmlparser.py
```

The `lfsbuilder` main directory contains the source code files and the main configuration file. The source code files are listed below:

* `actions.py`: custom actions for the different command line arguments.
* `builders.py`: logic to build a components list.
* `cli.py`: command line interface. Uses Python `argparse` native library.
* `components.py`: required logic for building a component, whether it requires compilation or not.
* `config.py`: main configuration file. Several of the options are available as cli options.
* `downloader.py`: takes care of downloading books' XML files and source code of components.
* `lfsbuilder.py`: main file of the tool. User interacts with it.
* `printer.py`: defines different functions for printing messages.
* `tools.py`: implements multiple functions that are used during the build process as read/write files, doing subsitutions in files, execute programs, etc.
* `xmlparser.py`: logic to read books' XML files and write each constructor's commands file.

