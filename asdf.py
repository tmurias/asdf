#! /usr/bin/env python3
"""
Tool for mapping shortcuts to directories.

Add shortcuts:
    $ asdf add project1 ~/projects/somewhere/somewhereelse/project1
    Adding shortcut project1
    $ asdf add project2 ~/projects/project2/p2
    Adding shortcut project2

View all shortcuts:
    $ asdf list
    project1 -> ~/projects/somewhere/somewhereelse/project1
    project2 -> ~/projects/project2/p2

Get directory for specific shortcut:
    $ asdf dir project2
    ~/projects/project2/p2

Open shortcut directory in new terminal:
    $ asdf open project2

Delete shortcut:
    $ asdf delete project1
    Deleted shortcut project1

Edit the shortcut file manually:
    $ asdf master
"""
import os
from pathlib import Path
import subprocess
import sys

SCF_FILEDIR = os.path.join(Path.home(), ".asdf")
SCF_FILENAME = os.path.join(SCF_FILEDIR, "shortcuts.csv")


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        error("1-3 arguments needed, run 'asdf help' for usage")

    asdf_arg = sys.argv[1].strip()
    if asdf_arg == "open":
        # asdf open <name>
        if len(sys.argv) != 3:
            error("usage - asdf open <name>")
        shortcut_arg = sys.argv[2].strip()
        validate_shortcut_name(shortcut_arg)
        output = asdf_open(shortcut_arg)
        if output:
            print(output)
    elif asdf_arg == "add":
        # asdf add <name> <path>
        if len(sys.argv) != 4:
            error("usage - asdf add <name> <path>")
        shortcut_arg = sys.argv[2].strip()
        validate_shortcut_name(shortcut_arg)
        path_arg = sys.argv[3].strip()
        output = asdf_add(shortcut_arg, path_arg)
        if output:
            print(output)
    elif asdf_arg == "list":
        # asdf list
        if len(sys.argv) != 2:
            error("too many arguments")
        output = asdf_list()
        if output:
            print(output)
    elif asdf_arg == "delete":
        # asdf delete <name>
        if len(sys.argv) != 3:
            error("usage - asdf open <name>")
        shortcut_arg = sys.argv[2].strip()
        validate_shortcut_name(shortcut_arg)
        output = asdf_delete(shortcut_arg)
        if output:
            print(output)
    elif asdf_arg == "master":
        # asdf master (manually edit the shortcut file)
        if len(sys.argv) != 2:
            error("too many arguments")
        output = asdf_master()
        if output:
            print(output)
    elif asdf_arg == "dir":
        # asdf dir <name>
        if len(sys.argv) != 3:
            error("usage - asdf dir <name>")
        shortcut_arg = sys.argv[2].strip()
        validate_shortcut_name(shortcut_arg)
        output = asdf_dir(shortcut_arg)
        if output:
            print(output)
    elif asdf_arg == "help":
        # asdf help
        print("asdf usage:")
        print("  asdf list")
        print("  asdf add <name> <path>")
        print("  asdf open <name>")
        print("  asdf dir <name>")
        print("  asdf delete <name>")
        print("  asdf master")
        print("  asdf help")
    else:
        err_msg = []
        err_msg.append("second arg must be one of the following:")
        err_msg.append("  list")
        err_msg.append("  add")
        err_msg.append("  open")
        err_msg.append("  dir")
        err_msg.append("  delete")
        err_msg.append("  master")
        err_msg.append("  help")
        error("\n".join(err_msg))


def validate_shortcut_name(sc_name):
    for c in sc_name:
        if not c.isalpha() and not c.isnumeric() and c != "_" and c != "-":
            error("invalid shortcut name, only letters, numbers, _, -")


def asdf_open(shortcut_name):
    if not os.path.exists(SCF_FILENAME):
        return "Shortcut " + shortcut_name + " does not exist"
    shortcuts = csv_to_dict(SCF_FILENAME)
    if shortcut_name not in shortcuts:
        error("shortcut doesn't exist: " + shortcut_name)
    shortcut_dir = shortcuts[shortcut_name]
    if os.path.exists(shortcut_dir) and os.path.isdir(shortcut_dir):
        open_shortcut(shortcut_dir)
    else:
        error("invalid path: " + shortcut_dir)


def asdf_add(shortcut_name, shortcut_path):
    if not os.path.exists(shortcut_path):
        error("path doesn't exist: " + shortcut_path)

    # Make ~/.asdf directory if it doesn't exist
    if not os.path.exists(SCF_FILEDIR):
        os.makedirs(SCF_FILEDIR)

    # Write (or update) the entry in the shortcuts file
    shortcuts = csv_to_dict(SCF_FILENAME)
    if shortcut_name in shortcuts:
        output = "Updating " + shortcut_name
    else:
        output = "Adding shortcut " + shortcut_name
    shortcuts[shortcut_name] = shortcut_path
    dict_to_csv(shortcuts, SCF_FILENAME)
    return output


def asdf_list():
    if os.path.exists(SCF_FILENAME):
        shortcuts = csv_to_dict(SCF_FILENAME)
        return get_shortcut_list(shortcuts)
    else:
        return "No shortcuts"


def asdf_delete(shortcut_name):
    if os.path.exists(SCF_FILENAME):
        shortcuts = csv_to_dict(SCF_FILENAME)
        if shortcut_name in shortcuts:
            del shortcuts[shortcut_name]
            dict_to_csv(shortcuts, SCF_FILENAME)
            return "Deleted shortcut " + shortcut_name
        else:
            return "Shortcut " + shortcut_name + " does not exist"
    else:
        return "Shortcut " + shortcut_name + " does not exist"


def asdf_master():
    subprocess.call(['vi', SCF_FILENAME])


def asdf_dir(shortcut_name):
    if os.path.exists(SCF_FILENAME):
        shortcuts = csv_to_dict(SCF_FILENAME)
        if shortcut_name in shortcuts:
            return shortcuts[shortcut_name]
        else:
            return "Shortcut " + shortcut_name + " does not exist"
    else:
        return "Shortcut " + shortcut_name + " does not exist"


def open_shortcut(scdir):
    bash_cmd = "gnome-terminal --working-directory=" + scdir + " &"
    process = subprocess.Popen(bash_cmd.split(), stdout=subprocess.PIPE)
    _, err = process.communicate()
    if err:
        error("failed to open terminal")


def csv_to_dict(filename):
    shortcuts = dict()
    if os.path.exists(filename):
        with open(filename, "r") as csv_file:
            for line in csv_file:
                sc = line.strip().split(",")
                if len(sc) == 2:
                    sc_name = sc[0]
                    sc_path = sc[1]
                    shortcuts[sc_name] = sc_path
    return shortcuts


def dict_to_csv(shortcuts, filename):
    with open(filename, "w+") as csv_file:
        for sc_name, sc_path in shortcuts.items():
            csv_file.write(sc_name + "," + sc_path + "\n")


def get_shortcut_list(shortcut_dict):
    ls = []
    for sc in sorted(shortcut_dict):
        ls.append(sc + " -> " + shortcut_dict[sc])
    return "\n".join(ls)


def error(msg):
    print("Error: " + str(msg))
    sys.exit()


if __name__ == "__main__":
    main()
