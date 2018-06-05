"""
tools.py

Common functions.
"""
import os
import sys
import subprocess
import shlex
import fnmatch
import tarfile
import zipfile
import pwd
import shutil
import importlib
import pprint
import yaml

import config
import printer


def write_file(filename, text, mode="w"):
    """
    Write file 'filename' with 'text' content.
    Remove 'filename' if exists.
    """
    # If file exists, delete it
    if os.path.exists(filename):
        os.remove(filename)

    fp = open(filename, mode)
    fp.write(text)
    fp.close()


def read_file(filename, mode="r"):
    """
    Read content from 'filename' if exists and return it content.
    """
    # If file exists, read it
    if os.path.exists(filename):
        fp = open(filename, mode)
        text = fp.read()
        fp.close()
        return text
    else:
        msg = "tools.read_file: file '{f}' not found". format(f=filename)
        printer.error(msg)


def backup_file(filepath):
    """
    Backup file 'filepath' by copying it in case backup file
    do not exists already.

    Add '.bck' suffix to the result file.
    """
    new_filepath = "{f}.bck".format(f=filepath)

    # If backup do not exists already
    if (os.path.exists(new_filepath)) is False:
        copy_file(filepath, new_filepath)


def restore_backup_file(filepath):
    """
    Restore backup to 'filepath' in case '/path/to/filepath.bck' file exists.
    """
    old_filepath = "{f}.bck".format(f=filepath)
    # If backup exists
    if os.path.exists(old_filepath):
        os.remove(filepath)
        copy_file(old_filepath, filepath)
        os.remove(old_filepath)


def copy_file(src, dest):
    """
    Copy 'src' file to 'dest'.
    """
    if src != dest:
        shutil.copyfile(src, dest)
    else:
        printer.error("tools.copy_file: 'src' and 'dest' are the same.")


def add_text_to_file(filename, text, at_the_beginning=False):
    """
    Add 'text' at the end the existing file 'filename' or
    writes it from scratch if not.

    It is also possible to add text at the beginning instead.
    """
    if os.path.exists(filename):
        previous_text = read_file(filename)

        if at_the_beginning is True:
            new_text = "{t}\n{p}".format(t=text, p=previous_text)
        else:
            new_text = "{p}\n{t}".format(t=text, p=previous_text)

        write_file(filename, new_text)
    else:
        # Target file do not exists, simply write it from scratch
        write_file(filename, text)


def substitute_in_file(filename, old, new):
    """
    Subsitute 'old' with 'new' in 'filename' content.
    """
    # If file exists, read it, substitute and overwrite
    original_text = read_file(filename)
    new_text = original_text.replace(old, new)
    write_file(filename, new_text)


def substitute_multiple_in_file(filename, substitution_list):
    """
    Do multiple substitutions in file 'filename' from
    'subsitution_list'.

    'subsitution_list must have an even number or elements.
    """
    # Check 'substitution_list' has an even number of elements.
    if len(substitution_list) % 2 != 0:
        msg = """The substitution list is not valid. Number of elements: \
{length}.
Please ensure you didn't miss any element, this parameter should have an \
even length."""
        msg = msg.format(length=len(substitution_list))
        printer.error(msg)

    for old, new in zip(substitution_list[0::2], substitution_list[1::2]):
        substitute_in_file(filename, old, new)


def modify_blfs_component_bootscript_install(cmd):
    """
    Modify bootscript installation steps for 'blfs' book components.
    """
    # Include bootscript installation steps
    # using the provided 'cmd' as base line
    text = """
# Install bootscript
# 1. Extract 'blfs-bootscripts' tarball and 'cd' in
cd @@LFS_SOURCES_DIRECTORY@@
tar xf blfs-bootscripts-@@LFS_BLFS_BOOTSCRIPTS_VERSION@@.tar.*
cd blfs-bootscripts-@@LFS_BLFS_BOOTSCRIPTS_VERSION@@

# 2. Install required service bootscript
{c}

# 3. Return to the 'sources' directory and remove the 'blfs-bootscripts' directory
cd @@LFS_SOURCES_DIRECTORY@@
rm -rf blfs-bootscripts-@@LFS_BLFS_BOOTSCRIPTS_VERSION@@
""".format(c=cmd)

    return text


def substitute_in_list(objective_list, element, substitution):
    """
    Substitute every 'element' occurrences with 'substitution' in the 'objective_list'.
    """
    while objective_list.count(element) > 0:
        # Get the 'element' index
        index = objective_list.index(element)
        # We replace the original list, not a copy at index
        objective_list.remove(element)
        objective_list[index:index] = substitution


def remove_and_add_element(objective_list, element, index=None):
    """
    Remove 'element' occurrences in the 'objective_list' and add it
    at the required position. Add at the end by default.
    """
    try:
        objective_list.remove(element)
    except ValueError:
        pass
    finally:
        if index is None:
            objective_list.append(element)
        else:
            objective_list.insert(index, element)


def remove_elements(objective_list, elements):
    """
    Remove multiple 'elements' in the 'objective_list'.
    """
    for element in elements:
        remove_element(objective_list, element)


def remove_element(objective_list, element):
    """
    Remove 'element' in the 'objective_element'.
    """
    if is_element_present(objective_list, element) is True:
        objective_list.remove(element)


def remove_all_and_add_element(objective_list, element, index=None):
    """
    Remove every 'element' occurrences in the 'objective_list' and add it
    at the required position. Add at the end by default.
    """

    while objective_list.count(element) > 1:
        # Remove element
        objective_list.remove(element)

    # There is only one 'element' in the 'objective_list'.
    remove_and_add_element(objective_list, element, index)


def get_element_index(objective_list, element, not_present=None):
    """
    Return 'element' position in 'objective_list' or 'not_present'.
    """
    try:
        index = objective_list.index(element)
    except ValueError:
        index = not_present

    return index


def is_element_present(objective_list, element):
    """
    Check if 'element' is present or not in the 'objective_list'.
    """
    result = False
    if element in objective_list:
        result = True

    return result


def disable_commands(commands_list):
    """
    Generate a substitution list to disable book's specified commands list by adding
    the 'remap=lfsbuilder_disable' attribute to the XML 'userinput' element.
    """
    result = []
    userinput_xml_tag = "<userinput>"
    disable_remap_attribute = "<userinput remap=\"lfsbuilder_disabled\">"

    for command in commands_list:
        if command.startswith("<userinput") is True:
            # XML tag was provided. Substitute with the
            # disabled 'remap' attribute
            aux_cmd = command.split(">")[1]
            cmd = "{d}{c}".format(d=disable_remap_attribute,
                                  c=aux_cmd)
        else:
            # User didn't provide XML attribute for command,
            # so we add it and then we disable it.
            # We are supposing it doesn't require a 'remap' attribute
            command = "{u}{c}".format(u=userinput_xml_tag,
                                      c=command)
            cmd = command.replace(userinput_xml_tag, disable_remap_attribute)

        # Add substitution strings to the 'result' list
        result.append(command)
        result.append(cmd)

    return result


def comment_out(comment_out_list, comment_symbol="#"):
    """
    Comments out strings from files by preceding the 'comment_symbol'
    'comment_out_list': elements to comment out
    'comment_symbol': symbol to precede strings with.
    """
    result = []

    for element in comment_out_list:
        result.append(element)
        commented_line = "{c} {e}".format(c=comment_symbol,
                                          e=element)
        result.append(commented_line)

    return result


def read_recipe_file(component_name, directory="components"):
    """
    Read YAML recipe file for the 'component_name' component. This recipe is placed
    under the 'recipes' directory.
    """
    filename = "{c}.yaml".format(c=component_name)
    recipe_path = os.path.realpath(os.path.join("recipes", directory,
                                                component_name, filename))
    recipe_data = {}

    if os.path.exists(recipe_path) is False:
        # Try "yml" instead of "yaml"
        filename = "{c}.yml".format(c=component_name)
        recipe_path = os.path.realpath(os.path.join("recipes", directory,
                                                    component_name, filename))
        # Error if do not exists
        if (os.path.exists(recipe_path)) is False:
            msg = "Error reading recipe. File '{f}' do not exists"
            msg = msg.format(f=recipe_path)
            printer.error(msg)

    # File exists, so read it
    fp = open(recipe_path, "r")
    recipe_data = yaml.load(fp)
    fp.close()

    return recipe_data


def read_functions_file(component_name,
                        filename="functions.py",
                        directory="components"):
    """
    Import the 'functions.py' functions file for the 'component_name' component if exists.
    """
    module = None
    functions_file = os.path.realpath(os.path.join("recipes", directory,
                                                   component_name, filename))

    if os.path.exists(functions_file):
        unix_module_path = "recipes/{d}/{c}/{f}".format(d=directory,
                                                        c=component_name,
                                                        f=filename)

        directory, module_name = os.path.split(unix_module_path)
        module_name = os.path.splitext(module_name)[0]

        path_bck = list(sys.path)
        sys.path.insert(0, directory)

        try:
            module = importlib.import_module(module_name, directory)

            # Remove the 'functions' module we have just imported
            # from the 'sys.module dictionary so we can import a
            # new module later on. If not, 'module' will always be
            # the first 'functions.py' module it has been imported during
            # the program execution
            del sys.modules[module_name]
        finally:
            # restore
            sys.path[:] = path_bck

    return module


def find_file(base_directory, pattern):
    """
    Search for a file in the 'base_directory' that match 'pattern'.
    """
    result = []
    for value in sorted(os.listdir(base_directory)):
        if fnmatch.fnmatch(value, pattern):
            result.append(os.path.join(base_directory, value))

    # Return 'None' if not found
    if is_empty_list(result) is True:
        result = None
    else:
        # List to string
        result = ''.join(result[0])

    return result


def find_file_recursive(base_directory, pattern):
    """
    Search recursively for a file in the 'base_directory' that match 'pattern'.
    """
    result = []
    files_list = [os.path.join(rootfolder, filename) for
                  rootfolder, subfolder, filenames in
                  os.walk(base_directory) for filename in filenames]

    for filename in files_list:
        if fnmatch.fnmatch(os.path.basename(filename), pattern):
            result.append(filename)

    return result


def find_directory(base_directory, pattern):
    """
    Search for a directory in the 'base_directory' that match 'pattern'.
    """
    result = []
    for value in os.listdir(base_directory):
        # If it is a directory and pattern matches
        if os.path.isdir(os.path.join(base_directory, value)) and \
           fnmatch.fnmatch(value, pattern):
            result.append(os.path.join(base_directory, value))

    # List to string
    result = ''.join(result)

    # Return 'None' if not found
    if result == "":
        result = None

    return result


def create_directory(directory_path):
    """
    Create directory if it does not exist.
    """
    if (os.path.exists(directory_path)) is False:
        os.mkdir(directory_path)


def demote_user(user_id, user_gid):
    """
    Demote current user by the one identified with 'user_id' and 'user_gid' so
    we can run a command as a different user.

    Return a function reference.
    """
    def result():
        """
        Set UID and GID attributes
        """
        os.setgid(user_gid)
        os.setuid(user_id)
    return result


def run_program(program_to_run):
    """
    Run 'program_to_run' and return the subprocess reference to be processed by the
    method which call this one.
    """
    command_to_run = shlex.split(program_to_run)
    p = subprocess.Popen(command_to_run,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return p


def run_program_as_user(program_to_run, username):
    """
    Run 'program_to_run' as the 'username' user.
    """
    # Get system values for the username
    pw_record = pwd.getpwnam(username)
    user_id = pw_record.pw_uid
    user_gid = pw_record.pw_gid

    command_to_run = shlex.split(program_to_run)
    p = subprocess.Popen(command_to_run,
                         preexec_fn=demote_user(user_id,
                                                user_gid),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return p


def run_program_with_output(program_to_run, username=None):
    """
    Run 'program_to_run' printing the info to the standard output.
    """
    if username is None:
        p = run_program(program_to_run)
    else:
        p = run_program_as_user(program_to_run, username)

    for line in iter(p.stdout.readline, b''):
        # Remove any 'newline' character if present
        print line.rstrip('\n')

    # Wait for the running command to finish
    p.wait()
    if p.returncode != 0:
        msg = "Command '{pr}' failed to run. Return code: '{r}'"
        msg = msg.format(pr=program_to_run,
                         r=str(p.returncode))
        printer.error(msg)


def run_program_without_output(program_to_run, username=None):
    """
    Run 'program_to_run' without printing anything to the standard output.
    """

    if username is None:
        p = run_program(program_to_run)
    else:
        p = run_program_as_user(program_to_run, username)

    # Print to /dev/null
    new_target = open(os.devnull, "w")
    old_target = sys.stdout
    sys.stdout = new_target

    for line in iter(p.stdout.readline, b''):
        # do nothing
        continue

    # Continue printing in console
    sys.stdout = old_target

    p.wait()
    if p.returncode != 0:
        msg = "Command '{pr}' failed to run. Return code: '{r}'"
        msg = msg.format(pr=program_to_run,
                         r=str(p.returncode))
        printer.error(msg)


def run_program_into_chroot(program_to_run, base_directory):
    """
    Run 'program_to_run' into the 'base_directory' previously converted in a chroot environment.

    Get out of the chroot environment once 'program_to_run' has run.
    """
    real_root = os.open("/", os.O_RDONLY)
    os.chroot(base_directory)
    # Removed 'os.chdir' call to run commands into chroot from directory
    # we were previously to call 'chroot'. Normally 'extracted_directory'
    # os.chdir("/")

    # Chrooted environment
    if config.VERBOSE is True:
        run_program_with_output(program_to_run)
    else:
        run_program_without_output(program_to_run)

    # Back to old root
    os.fchdir(real_root)
    os.chroot(".")
    os.close(real_root)


def get_class(class_name):
    """
    Get class reference of the 'class_name' class so we can instanciate a object
    dinamycally at runtime providing a 'class_name' such as 'module.ClassName'.
    """
    parts = class_name.split('.')

    # Ensure module is a string
    module = ".".join(parts[:-1])
    m = __import__(module)

    for comp in parts[1:]:
        m = getattr(m, comp)

    return m


def generate_placeholder(key):
    """
    Generate '@@LFS_' placeholder for 'key'.
    """
    value = key.upper().replace("-", "_")
    return "@@LFS_{v}@@".format(v=value)


def extract_tarfile(filename, destination, extension=None):
    """
    Extract provided 'filename' tarfile to the 'destination' directory.
    """
    if extension is None:
        tar = tarfile.open(filename, "r:*")
        tar.extractall(path=destination)
        tar.close()
    elif extension == "xz":
        cmd = "tar -xf " + filename + " -C " + destination
        run_program_without_output(cmd)


def extract_zipfile(filename, destination):
    """
    Extract provided 'filename' zipfile to the 'destination' directory.
    """
    zipf = zipfile.ZipFile(filename, "r")
    zipf.extractall(destination)
    zipf.close()


def extract(filename, destination=None):
    """
    Extract 'filename' compressed file to the 'destination' directory.
    """
    if destination is None:
        destination = os.getcwd()

    # Show message info
    msg = "Extracting file '{f}' into '{d}'"
    msg = msg.format(f=os.path.basename(filename),
                     d=destination)
    printer.substep_info(msg)

    # File extension
    ext = os.path.splitext(filename)[1][1:]

    if tarfile.is_tarfile(filename) is True:
        extract_tarfile(filename, destination)
    elif zipfile.is_zipfile(filename) is True:
        extract_zipfile(filename, destination)
    elif ext == "xz":
        extract_tarfile(filename, destination, ext)
    else:
        msg = "tools.extract: archive '{f}' extension not recognized"
        msg = msg.format(f=filename)
        printer.error(msg)

# ---


def check_user_exists(username):
    """
    Check 'username' exists.
    """
    result = False
    try:
        pwd.getpwnam(username)
        result = True
    except KeyError:
        pass

    return result


def set_owner_and_group(filename, username, groupname=None):
    """
    Set 'username' as owner and 'groupname' as group attributes for 'filename'.
    """
    if groupname is None:
        groupname = username

    # Get username attributes
    pw_record = pwd.getpwnam(username)
    owner_id = pw_record.pw_uid
    pw_record = pwd.getpwnam(groupname)
    group_gid = pw_record.pw_gid
    # Set owner and group
    os.chown(filename, owner_id, group_gid)


def set_recursive_owner_and_group(directory, username, groupname=None):
    """
    Set 'username' as owner and 'groupname' as group attributes recursively for everything
    under 'directory'.
    """
    if groupname is None:
        groupname = username

    # Set permission for the top level directory
    set_owner_and_group(directory, username, groupname)

    # Set recursively for what is inside
    for root_dir, dirs, files in os.walk(directory):
        # Join everything found into a single list and iterate
        file_list = dirs + files
        for f in file_list:
            set_owner_and_group(os.path.join(root_dir, f),
                                username,
                                groupname)
# ---


def check_lfs_builders_tuple(t, s, c):
    """
    This function checks if provided 'lfs' book's builders combination
    is valid (order doesn't matter) by implementing solution
    for the below Karnaugh map:

    \ sc
  t  \   00   01   10   11
      +____________________+
  0   |  1  | 1  | 1  | 1  |
      +-----+----+----+----+
  1   |  1  | 0  | 1  | 1  |
      +-----+----+----+----+

    """
    return (not(t)) or s or (not(c))


def check_lfs_builders_order(t, s, c, m, la):
    """
    This function checks if provided 'lfs' book's builders combination
    is valid (order does matter) by implementing solution for the corresponding
    5 variable's Karnaugh map where inputs are:

t: whether the 'toolchain' builder is pretended to be built or not

s: whether the 'system' builder is pretended to be built or not

c: whether the 'configuration' builder is pretended to be built or not

m: whether the 'toolchain' builder is pretended to be built first or not.
That's it, if its index value is the minimum between them.

la: whether the 'system' builder is pretended to be built before
the 'configuration' builder or not. That's true if its index value
is the minimum between them.

    """
    # Ensure we are getting boolean values as input
    t = bool(t)
    s = bool(s)
    c = bool(c)
    m = bool(m)
    la = bool(la)

    return (not(t) and la) or \
           (not(s) and not(c)) or \
           (not(t) and not(c)) or \
           (not(t) and not(s) and m) or \
           (not(t) and not(s) and not(m)) or \
           (s and m and la) or \
           (not(c) and m)


def check_meson_builder_combination(m, sv, sd):
    """
    This function checks if provided 'boot manager' and 'meson builder' selected
    or not combination is valid by implementing solution for the below Karnaugh map:

    \ sv,sd
  m  \   00   01   11   10
      +____________________+
  0   |  0  | 0  | 0  | 1  |
      +-----+----+----+----+
  1   |  0  | 1  | 0  | 1  |
      +-----+----+----+----+

    """
    return (m and not(sv) and sd) or (sv and not(sd))


def add_to_dictionary(dictionary, key, value, concat="\n"):
    """
    Add 'value' to the 'key' in 'dictionary'. Concat current values unless
    'concat' argument is 'False'.
    """
    # If key exists in dictionary, then concatenate values
    # and update dictionary
    if key in dictionary and \
       dictionary[key] is not None and \
       concat is not False:
        value = dictionary[key] + concat + value

    dictionary[key] = value


def join_dicts(*dict_args):
    """
    Given any number of dicts, copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def is_empty_list(li):
    """
    Check if provided list 'li' is empty.
    """
    empty = False
    if not li:
        empty = True

    return empty


def list_from_file(filename):
    """
    Generate list from lines in 'filename'.
    """
    return [line for line in read_file(filename).split("\n")]


def write_xmlfile(filename, text):
    """
    Write XML 'filename' with XML DOM tree provided in 'text'.
    """
    import xml.dom.minidom
    xml = xml.dom.minidom.parseString(text)
    write_file(filename, xml.toprettyxml())


def is_mount(directory):
    """
    Check if 'directory' is mount or not. We use the Python built-in method 'os.path.ismount'
    and also check '/proc/mounts' file because Python do not recognize a
    directory as mounted in case the parent directory is not mounted too ('--bind' option).
    https://bugs.python.org/issue29707
    """
    proc_mounts = "/proc/mounts"
    result = False

    # First check using Python's 'ismount()'. If not, try checking '/proc/mounts' instead.
    if os.path.ismount(directory) is True:
        result = True

    elif os.path.exists(proc_mounts) is True:
        # .- read 'proc_mounts' into list
        data = read_file(proc_mounts).rstrip("\n").split("\n")

        # .- get mount points on second column
        mount_points = [line.split(" ")[1] for line in data]

        # .- check if directory is in 'mount_points'
        if directory in mount_points:
            result = True

    else:
        # Default value is already 'False'
        pass

    return result


def pretty_print(element):
    """
    Pretty print 'element'.
    """
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(element)
