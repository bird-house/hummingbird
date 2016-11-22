import subprocess

import logging
logger = logging.getLogger(__name__)


def ncdump(dataset):
    '''
    Returns the CDL of the dataset

    Code taken from https://github.com/ioos/compliance-checker-web
    '''

    try:
        output = subprocess.check_output(['ncdump', '-h', dataset])
        if not isinstance(output, str):
            output = output.decode('utf-8')
        lines = output.split('\n')
        # replace the filename for safety
        dataset_id = 'uploaded-file'
        lines[0] = 'netcdf %s {' % dataset_id
        filtered_lines = '\n'.join(lines)
    except Exception:
        logger.exception("could not generate ncdump")
        return "Error generating ncdump"
    return filtered_lines
