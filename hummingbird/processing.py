import os
import glob
import subprocess
from subprocess import check_output, CalledProcessError

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
        # decode to ascii
        filtered_lines = [str(line) + '\n' for line in lines]
    except Exception:
        logger.exception("could not generate ncdump")
        return "Error: generating ncdump failed"
    return filtered_lines


def hdh_cf_check(filename, version="auto"):
    # TODO: maybe use local file path
    filename = os.path.abspath(fix_filename(filename))
    cmd = ["dkrz-cf-checker", filename]
    if version != "auto":
        cmd.extend(['-C', version])
    try:
        output = check_output(cmd, stderr=subprocess.STDOUT)
    except CalledProcessError as err:
        logger.exception("cfchecks failed!")
        return "Error: cfchecks failed: {0}. Output: {0.output}".format(err)
    return output


def hdh_qa_checker(filename, project, qa_home=None):
    # TODO: maybe use local file path
    filename = os.path.abspath(fix_filename(filename))

    # create qa_home
    # qa_home = os.path.join(config.cache_path(), "qa_dkrz")
    if not qa_home:
        qa_home = os.path.abspath("./work")
    make_dirs(qa_home)

    cmd = ["qa-dkrz", "-P", project]
    if qa_home:
        cmd.append("--work=" + qa_home)
    cmd.append(filename)
    try:
        check_output(cmd, stderr=subprocess.STDOUT)
    except CalledProcessError as err:
        logger.exception("qa checker failed!")
        msg = "qa checker failed: {0}. Output: {0.output}".format(err)
        raise Exception(msg)

    results_path = os.path.join("QA_Results", "check_logs")
    if not os.path.isdir(results_path):
        raise Exception("QA results are missing.")

    # output logfile
    logs = glob.glob(os.path.join(results_path, "*.log"))
    if not logs:
        logs = glob.glob(os.path.join(results_path, ".*.log"))
    if logs:
        # use .txt extension
        logfile = logs[0][:-4] + '.txt'
        os.link(logs[0], logfile)
    else:
        raise Exception("could not find log file.")
    return logfile, results_path
