# LFSBuilder

The _[Linux from Scratch](http://www.linuxfromscratch.org/)_ project provides a step-by-step instructions for building your own customized Linux-based distribution from source code. Apart from the learning experience and because this is a long repetitive process, the _Linux from Scratch_ project developers provide users with an automation tool called _[jhalfs](http://www.linuxfromscratch.org/alfs/)_.

LFSBuilder is a Python program that has the same purpose, to automatically build a Linux from Scratch system. It also can be used with the _[Beyond Linux from Scratch](http://www.linuxfromscratch.org/blfs/)_ book. This tool is designed under the _[Object Oriented Programming](https://en.wikipedia.org/wiki/Object-oriented_programming)_ paradigm to simplify the code structure and also implements an extra customizable layer on top of the core functionality of the tool. This extra layer allows users to build an operating system that fits the requirements of multiple use cases.

The main elements of LFSBuilder are two: builders and components. A `builder` is an object capable of building one or more `components` and represents, in concept, any of the main chapters of the _Linux from Scratch_ and _Beyond Linux from Scratch_ books. It is also possible to define your own builders so you can do specific tasks or build your own components. A `component` represents a real element that interacts with the final system, either to add a new component (e.g. `gcc`, `curl`, `bash` or `ssh`) or to accomplish other tasks (e.g. mount the required system directories or generate the `.img` file in which the system will be built into by default).

The extra customization layer is defined in what I called a _recipe_, a little element that allows you to define any of the main elements and to customize its actions by overwriting some core functions if necessary. More info about the recipes system can be found in its own section.

LFSBuilder scope is not restricted to the Linux from Scratch project and can also be used to build your own components.

LFSBuilder development started during the summer of 2016 as part of my Telecommunications Engineering degree's thesis. It was qualified in September of 2018, and from March 2019 is publicly available. The original thesis PDF document is available, in Spanish only, at the [Universidad de Sevilla e-REdING website](http://bibing.us.es/proyectos/buscar/gonzalo+gomez+gracia/en/todo/and//en/todo/limitado_a/todos/entre/1970/y/2019///1).

This is a project in constant development and licensed under the [AGPL3 (GNU AFFERO GENERAL PUBLIC LICENSE)](https://www.gnu.org/licenses/agpl-3.0.en.html) Open Source license.
