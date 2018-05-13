
import os
import sys
import subprocess
import shlex
import fnmatch
import tarfile
import zipfile
import pwd
import shutil
import ctypes
import yaml
import importlib

import printer

# Functions and utilities

# ---

def write_file (filename, text, mode = "w"):
    # If file exists, delete it
    if os.path.exists(filename):
        os.remove(filename)

    fp = open(filename, mode)
    fp.write(text)
    fp.close()

def read_file (filename, mode = "r"):
    # If file exists, read it
    if os.path.exists(filename):
        fp = open(filename, mode)
        text = fp.read()
        fp.close()
        return text
    else:
        msg = "File " + filename + " not found."
        printer.error(msg)

def backup_file(filepath):
    new_filepath = "{f}.bck".format(f=filepath)

    # If backup do not exists already
    if os.path.exists(new_filepath) == False:
        copy_file(filepath, new_filepath)

def restore_backup_file(filepath):
    old_filepath = "{f}.bck".format(f=filepath)
    # If backup exists
    if os.path.exists(old_filepath) == True:
        os.remove(filepath)
        copy_file(old_filepath, filepath)
        os.remove(old_filepath)

def copy_file (src, dest):
    if src != dest:
        shutil.copyfile(src, dest)
    else:
        printer.error("tools.copy_file: 'src' and 'dest' are the same.")

def add_text_to_file (filename, text, at_the_beginning=False):
    if os.path.exists(filename):
        previous_text = read_file(filename)

        if at_the_beginning is True:
            new_text = "{t}\n{p}".format(t = text, p = previous_text)
        else:
            new_text = "{p}\n{t}".format(t = text, p = previous_text)

        write_file(filename, new_text)
    else:
        # Target file do not exists, simply write it from scratch
        write_file(filename, text)

def substitute_in_file (filename, old, new):
    # If file exists, read it, substitute and overwrite
    original_text = read_file(filename)
    new_text = original_text.replace(old, new)
    write_file(filename, new_text)


def substitute_multiple_in_file (filename, substitution_list):
    # Check 'substitution_list' has an even number of elements.
    if len(substitution_list) % 2 != 0:
            msg = """The substitution list is not valid. Number of elements: {length}.
Please ensure you didn't miss any element, this parameter should have an even length."""
            msg = msg.format(length = len(substitution_list))
            printer.error(msg)

    for old,new in zip(substitution_list[0::2], substitution_list[1::2]):
        substitute_in_file(filename, old, new)

def modify_blfs_component_bootscript_install(cmd):
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
    while objective_list.count(element) > 0:
        # Get the 'element' index
        index = objective_list.index(element)
        # We replace the original list, not a copy at index
        objective_list.remove(element)
        objective_list[index:index] = substitution

def remove_and_add_element(objective_list, element, index=None):
    # Add at the end by default
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
    for element in elements:
        remove_element(objective_list, element)

def remove_element(objective_list, element):
    if is_element_present(objective_list, element) is True:
        objective_list.remove(element)

def remove_all_and_add_element(objective_list, element, index=None):
    while objective_list.count(element) > 1:
        # Remove element
        objective_list.remove(element)

    else:
        remove_and_add_element(objective_list, element, index)

def get_element_index(objective_list, element, not_present=None):
    try:
        index = objective_list.index(element)
    except ValueError:
        index = not_present
    finally:
        return index

def is_element_present(objective_list, element):
    result = False
    if element in objective_list:
        result = True

    return result

def disable_commands(commands_list):
    result = []
    userinput_xml_tag = "<userinput>"
    disable_remap_attribute = "<userinput remap=\"lfsbuilder_disabled\">"

    for command in commands_list:
        if command.startswith("<userinput") is True:
            # XML tag was provided. Substitute with the disabled 'remap' attribute
            aux_cmd = command.split(">")[1]
            cmd = "{d}{c}".format(d = disable_remap_attribute,
                                  c = aux_cmd)
        else:
            # User didn't provide XML attribute for command,
            # so we add it and then we disable it.
            # We are supposing it doesn't require a 'remap' attribute
            command = "{u}{c}".format(u = userinput_xml_tag,
                                      c = command)
            cmd = command.replace(userinput_xml_tag, disable_remap_attribute)

        # Add substitution strings to the 'result' list
        result.append(command)
        result.append(cmd)

    return result

def comment_out(comment_out_list, comment_symbol = "#"):
    ## Comments out strings from files by preceding the 'comment_symbol'
    # 'comment_out_list': elements to comment out
    # 'comment_symbol': symbol to precede strings with.
    result = []

    for element in comment_out_list:
        result.append(element)
        comment_out = "{c} {e}".format(c = comment_symbol,
                                       e = element)
        result.append(comment_out)

    return result

def read_recipe_file(component_name, directory="components"):

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
        if os.path.exists(recipe_path) is False:
            msg = "Error reading recipe. File '{f}' do not exists".format(f=recipe_path)
            printer.error(msg)

    # File exists, so read it
    fp = open(recipe_path, "r")
    recipe_data = yaml.load(fp)
    fp.close()

    return recipe_data

def read_functions_file(component_name, filename="functions.py", directory="components"):

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

            # Remove the 'functions' module we have just imported from the 'sys.modules'
            # dictionary so we can import a new module later on. If not, 'module' will always be
            # the first 'functions.py' module it has been imported during the program execution
            del sys.modules[module_name]
        finally:
            sys.path[:] = path_bck # restore

    return module

def find_file (base_directory, pattern):
    result = []
    for value in os.listdir(base_directory):
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
    result = []
    files_list = [os.path.join(rootfolder, filename) for rootfolder, subfolder, filenames in os.walk(base_directory) for filename in filenames]

    for filename in files_list:
        if fnmatch.fnmatch(os.path.basename(filename), pattern):
            result.append(filename)

    return result

def find_directory (base_directory, pattern):
    result = []
    for value in os.listdir(base_directory):
        # If it is a directory and pattern matches
        if os.path.isdir(os.path.join(base_directory, value)) and fnmatch.fnmatch(value, pattern):
            result.append(os.path.join(base_directory, value))

    # List to string
    result = ''.join(result)

    # Return 'None' if not found
    if result == "":
        result = None

    return result

def create_directory(directory_path):
    # Create directory if it does not exist
    if os.path.exists(directory_path) == False:
        os.mkdir(directory_path)

# ---

def demote_user(user_id, user_gid):
    def result():
        os.setgid(user_gid)
        os.setuid(user_id)
    return result

def run_program (program_to_run):
    command_to_run = shlex.split(program_to_run)
    p = subprocess.Popen(command_to_run, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p

def run_program_as_user(program_to_run, username):
    # Get system values for the username
    pw_record = pwd.getpwnam(username)
    user_id = pw_record.pw_uid
    user_gid = pw_record.pw_gid

    command_to_run = shlex.split(program_to_run)
    p = subprocess.Popen(command_to_run, preexec_fn=demote_user(user_id, user_gid),
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p

def run_program_with_output (program_to_run, username = ""):
    if username == "":
        p = run_program(program_to_run)
    else:
        p = run_program_as_user(program_to_run, username)

    for line in iter(p.stdout.readline, b''):
        # Remove any 'newline' character if present
        print line.rstrip('\n')

    # Wait for the running command to finish
    p.wait()
    if p.returncode != 0:
        printer.error("Command \'" + program_to_run + "\' failed to run. Return code: " + str(p.returncode))

def run_program_without_output (program_to_run, username = ""):

    if username == "":
        p = run_program(program_to_run)
    else:
        p = run_program_as_user(program_to_run, username)

    # Print to /dev/null
    new_target = open(os.devnull, "w")
    old_target = sys.stdout
    sys.stdout = new_target

    for line in iter(p.stdout.readline, b''):
        # print line
        continue

    # Continue printing in console
    sys.stdout = old_target

    p.wait()
    if p.returncode != 0:
        printer.error("Command \'" + program_to_run + "\' failed to run. Return code: " + str(p.returncode))


def run_program_into_chroot (program_to_run, base_directory):
        real_root = os.open("/", os.O_RDONLY)
        os.chroot(base_directory)
        # Removed 'os.chdir' call to run commands into chroot from directory we were
        # previously to call 'chroot'. Normally 'extracted_directory'
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

# ---

def get_class (class_name):
    parts = class_name.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m

def generate_placeholder(key):
    value = key.upper().replace("-", "_")
    return "@@LFS_{v}@@".format(v=value)

def extract_tarfile (filename, destination, extension=""):
    if extension == "":
        tar = tarfile.open(filename, "r:*")
        tar.extractall(path=destination)
        tar.close()
    elif extension == "xz":
        cmd = "tar -xf " + filename + " -C " + destination
        run_program_without_output(cmd)

def extract_zipfile (filename, destination):
    zip = zipfile.ZipFile(filename, "r")
    zip.extractall(destination)
    zip.close()


def extract (filename, destination=""):
    if destination == "":
        destination = os.getcwd()

    # Show message info
    printer.substepInfo("Extracting file \'" + os.path.basename(filename) + "\' into \'" + destination + "\'")

    # File extension
    ext = os.path.splitext(filename)[1][1:]

    if tarfile.is_tarfile(filename) == True:
        extract_tarfile(filename, destination)
    elif zipfile.is_zipfile(filename) == True:
        extract_zipfile(filename, destination)
    elif ext == "xz":
        extract_tarfile(filename, destination, ext)
    else:
        printer.error("Archive \'" + filename + "\' extension not recognized")

# ---

def check_user_exists(username):
    result = False
    try:
        u = pwd.getpwnam(username)
        result = True
    except KeyError:
        pass

    return result

def set_owner_and_group(filename, username, groupname=None):
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
    if groupname is None:
        groupname = username

    # Set permission for the top level directory
    set_owner_and_group(directory, username, groupname)

    # Set recursively for what is inside
    for root_dir, dirs, files in os.walk(directory):
        # Join everything found into a single list and iterate
        file_list = dirs + files
        for f in file_list:
            set_owner_and_group(os.path.join(root_dir, f), username, groupname)
# ---

def add_to_dictionary(dictionary, key, value, concat="\n"):
    # If key exists in dictionary, then concatenate values and update dictionary
    if key in dictionary and dictionary[key] is not None and concat != False:
        value = dictionary[key] + concat + value

    dictionary[key] = value

def join_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

# ---
def is_empty_list(l):
    empty = False
    if not l:
        empty = True

    return empty

def list_from_file(filename):
    return [line for line in read_file(filename).split("\n")]

# ---
def write_xmlfile(filename, text):
    import xml.dom.minidom
    xml = xml.dom.minidom.parseString(text)
    write_file(filename, xml.toprettyxml())

def pretty_print(element):
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(element)

# ---
def mount(source, target, fs, options=''):
    ret = ctypes.CDLL('libc.so.6', use_errno=True).mount(source, target, fs, 0, options)
    if ret < 0:
        errno = ctypes.get_errno()
        raise RuntimeError("Error mounting {} ({}) on {} with options '{}': {}".
                           format(source, fs, target, options, os.strerror(errno)))

def umount(target):
    ret = ctypes.CDLL('libc.so.6', use_errno=True).umount(target, None)
    if ret < 0:
        errno = ctypes.get_errno()
        raise RuntimeError("Error umounting '{}' with error code: {}".format(target, os.strerror(errno)))
