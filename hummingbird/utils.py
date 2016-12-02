import os


def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def fix_filename(filename):
    if not filename.endswith(".nc"):
        new_name = filename + ".nc"
        os.rename(filename, new_name)
        filename = new_name
    return filename
