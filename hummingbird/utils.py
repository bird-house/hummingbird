import os

import logging
LOGGER = logging.getLogger("PYWPS")


def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def fix_filename(filename):
    if not filename.endswith(".nc"):
        new_name = filename + ".nc"
        os.rename(filename, new_name)
        filename = new_name
    return filename


def output_file(filename, addition=None, extension=None):
    extension = extension or 'nc'
    addition = addition or ''
    try:
        outfile = "{0}_{1}.{2}".format(
            os.path.basename(filename).split('.' + extension)[0],
            addition,
            extension)
    except Exception:
        LOGGER.debug("Could not generate output name.")
        _, outfile = tempfile.mkstemp(suffix=extension, prefix="output")
    return outfile
