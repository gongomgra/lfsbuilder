
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

import printer

# Functions and utilities

# ---

def write_file (filename, text):
    # If file exists, delete it
    if os.path.exists(filename):
        os.remove(filename)

    fp = open(filename, "w")
    fp.write(text)
    fp.close()

def read_file (filename):
    # If file exists, read it
    if os.path.exists(filename):
        fp = open(filename, "r")
        text = fp.read()
        fp.close()
        return text

def copy_file (src, dest):
    if src != dest:
        shutil.copyfile(src, dest)
    else:
        printer.error("dedalo.copy_file: 'src' and 'dest' are the same.")

def add_text_to_file (filename, text, at_the_beginning=0):
    if os.path.exists(filename):
        previous_text = read_file(filename)

        if at_the_beginning == 0:
            new_text = previous_text + "\n" + text
        else:
            new_text = text + "\n" + previous_text

        write_file(filename, new_text)
    else:
        # Target file do not exists, simply write it from scratch
        write_file(filename, text)

def substitute_in_file (filename, old, new):
    # If file exists, read it, substitute and overwrite
    original_text = read_file(filename)
    new_text = original_text.replace(old, new)
    write_file(filename, new_text)

# def substituteMultipleInFile (filename, oldList, newList):
#     for old,new in zip(oldList, newList):
#         substitute_in_file(filename, old, new)

def substitute_multiple_in_file (filename, substitution_list):
    for old,new in zip(substitution_list[0::2], substitution_list[1::2]):
        substitute_in_file(filename, old, new)

def find_file (base_directory, pattern):
    result = []
    for value in os.listdir(base_directory):
        if fnmatch.fnmatch(value, pattern):
            result.append(os.path.join(base_directory, value))

    # List to string
    result = ''.join(result)
    return result

def find_directory (base_directory, pattern):
    result = []
    for value in os.listdir(base_directory):
        # If it is a directory and pattern matches
        if os.path.isdir(os.path.join(base_directory, value)) and fnmatch.fnmatch(value, pattern):
            result.append(os.path.join(base_directory, value))

    # List to string
    result = ''.join(result)
    return result

def create_directory(directory_path):
    # Remove directory if exists
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)

    # Recreate it
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
 #   return iter(p.stdout.readline, b'')

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
    # new_target = open(os.devnull, "w")
    # old_target = sys.stdout
    # sys.stdout = new_target

    # for line in run_program(program_to_run):
    #     print line

    # sys.stdout = old_target

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
        # Removed 'os.chdir' call to run commands into chroot into directory we were previously to call 'chroot'
        # Normally 'extracted_directory'
        # os.chdir("/")

        # Chrooted environment
        sys.exit(0)
        run_program_with_output(program_to_run)

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


def apply_patch (filename):
    printer.substepInfo("Applying patchfile \'" + os.path.basename(filename) + "\'")
    cmd = "patch -N -p1 < " + filename
    text = """#!/bin/bash
""" + cmd
    write_file("patch.sh", text)
    cmd_aux = "bash patch.sh"
    # run_program_with_output (cmd_aux)
    run_program_without_output (cmd_aux)

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
    for rootDir, dirs, files in os.walk(directory):
        # Join everything found into a single list and iterate
        fileList = dirs + files
        for f in fileList:
            set_owner_and_group(os.path.join(rootDir, f), username, groupname)
        # for f in files:
        #     set_owner_and_group(os.path.join(rootDir, f), username, groupname)
# ---

def add_to_dictionary(dictionary, key, value, concat="\n"):
    # If key exists in dictionary, then concatenate values and update dictionary
    check = key in dictionary
    if check == True and concat != False:
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
