import os
import glob
import subprocess
from subprocess import check_output, CalledProcessError

from .utils import fix_filename, make_dirs

import logging
LOGGER = logging.getLogger("PYWPS")


def ncgen(cdl_file, output_file=None):
    '''
    Returns NetCDF file from CDL file.
    '''
    output_file = output_file or 'output.nc'

    try:
        subprocess.run(['ncgen', '-k', 'nc4', '-o', output_file, cdl_file], check=True)
    except Exception as err:
        LOGGER.error("Could not generate ncdump: {}".format(err))
        pass


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
        lines[0] = 'netcdf {} {{'.format(dataset_id)
        # decode to ascii
        filtered_lines = ['{}\n'.format(line) for line in lines]
    except Exception as err:
        LOGGER.error("Could not generate ncdump: {}".format(err))
        return "Error: generating ncdump failed"
    return filtered_lines


def cmor_tables_path():
    os.environ['UVCDAT_ANONYMOUS_LOG'] = 'no'
    import cmor
    tables_path = os.path.abspath(
        os.path.join(cmor.__file__, '..', '..', '..', '..', '..', 'share', 'cmip6-cmor-tables', 'Tables'))
    return tables_path


def cmor_tables():
    tables = glob.glob(os.path.join(cmor_tables_path(), 'CMIP6_*.json'))
    table_names = [os.path.basename(table)[0:-5] for table in tables]
    table_names.sort()
    return table_names


def cmor_dump_output(dataset, status, output, output_filename):
    import string
    if not isinstance(output, str):
        output = output.decode('utf-8')
    # show filename
    dataset_id = os.path.basename(dataset)  # 'uploaded-file'
    converted_lines = []
    converted_lines.append('## Checking NetCDF file {}\n\n'.format(dataset_id))
    if status is True:
        converted_lines.append("Dateset *passed* CMIP6 cmor checks:\n")
    else:
        converted_lines.append("Dateset *failed* CMIP6 cmor checks:\n")
    # decode to ascii
    for line in output.split('\n'):
        line = line.translate(None, '!')
        if chr(27) in line:
            continue
        if "In function:" in line:
            continue
        if "called from:" in line:
            continue
        line = line.strip()
        if not line:  # skip empty lines
            continue
        # remove non printable chars
        line = ''.join([x for x in line if x in string.printable])
        # error list option
        if line.startswith("Error:"):
            line = "\n* " + line
        converted_lines.append(str(line) + '\n')
    with open(output_filename, 'w') as fp:
        fp.writelines(converted_lines)


def cmor_checker(dataset, table='CMIP6_CV', variable=None, output_filename=None):
    output_filename = output_filename or 'out.txt'
    try:
        cmd = ['PrePARE']
        if variable:
            cmd.extend(['--variable', variable])
        table_path = os.path.join(cmor_tables_path(), table + '.json')
        cmd.append(table_path)
        cmd.append(dataset)
        LOGGER.debug("run command: %s", cmd)
        os.environ['UVCDAT_ANONYMOUS_LOG'] = 'no'
        output = check_output(cmd, stderr=subprocess.STDOUT)
        cmor_dump_output(dataset, True, output, output_filename)
    except CalledProcessError as err:
        LOGGER.warn("CMOR checker failed on dataset: %s", os.path.basename(dataset))
        cmor_dump_output(dataset, False, err.output, output_filename)
        return False
    return True


def hdh_cf_check(filename, version="auto"):
    # TODO: maybe use local file path
    filename = os.path.abspath(fix_filename(filename))
    cmd = ["dkrz-cf-checker", filename]
    if version != "auto":
        cmd.extend(['-C', version])
    try:
        output = check_output(cmd, stderr=subprocess.STDOUT)
    except CalledProcessError as err:
        LOGGER.exception("cfchecks failed!")
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
        LOGGER.exception("qa checker failed!")
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
