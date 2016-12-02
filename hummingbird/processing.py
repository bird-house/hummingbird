import os
from subprocess import check_output, CalledProcessError, STDOUT

from .utils import fix_filename, make_dirs

import logging
logger = logging.getLogger("PYWPS")


def ncdump(dataset):
    '''
    Returns the metadata of the dataset

    Code taken from https://github.com/ioos/compliance-checker-web
    '''

    try:
        output = check_output(['ncdump', '-h', dataset])
        if not isinstance(output, str):
            output = output.decode('utf-8')
        lines = output.split('\n')
        # replace the filename for safety
        dataset_id = os.path.basename(dataset)  # 'uploaded-file'
        lines[0] = 'netcdf %s {' % dataset_id
        filtered_lines = '\n'.join(lines)
    except Exception:
        logger.exception("could not generate ncdump")
        return "Error generating ncdump"
    return filtered_lines


def hdh_cf_check(filename, version="auto"):
    # TODO: maybe use local file path
    filename = os.path.abspath(fix_filename(filename))
    cmd = ["dkrz-cf-checker", filename]
    if version != "auto":
        cmd.extend(['-C', version])
    try:
        output = check_output(cmd)
    except CalledProcessError as err:
        logger.exception("cfchecks failed!")
        output = err.output
    return output


def hdh_qa_checker(filename, project, qa_home=None):
    # TODO: maybe use local file path
    filename = os.path.abspath(fix_filename(filename))

    # create qa_home
    # qa_home = os.path.join(config.cache_path(), "qa_dkrz")
    if not qa_home:
        qa_home = os.path.abspath("./qa_dkrz")
    make_dirs(qa_home)

    cmd = ["qa-dkrz", "-P", project]
    if qa_home:
        cmd.append("--work=" + qa_home)
    cmd.append(filename)
    try:
        check_output(cmd, stderr=STDOUT)
    except CalledProcessError as e:
        msg = "qa checker failed: %s" % (e.output)
        logger.error(msg)
        raise Exception(msg)
