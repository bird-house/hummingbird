import os
import shutil
from subprocess import check_output, CalledProcessError, STDOUT

from pywps.Process import WPSProcess
import logging
logger = logging.getLogger(__name__)

qa_task = """
PROJECT_DATA={1}/{0}
QC_RESULTS=results
PROJECT={0}
QC_CONF={0}_qc.conf
"""

def cf_check(nc_file):
    # TODO: maybe use local file path
    if not nc_file.endswith(".nc"):
        new_name = nc_file + ".nc"
        from os import rename
        rename(nc_file, new_name)
        nc_file = new_name
    cmd = ["dkrz-cf-checker", nc_file]
    try:
        output = check_output(cmd)
    except CalledProcessError as err:
        logger.exception("cfchecks failed!")
        output = err.output
    return output


class CFChecker(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier="qa_cfchecker",
            title="QA DKRZ CF Checker",
            version="0.5.3-1",
            abstract="Qualtiy Assurance Tools by DKRZ: cfchecker checks NetCDF files for compliance to the CF standard.",
            statusSupported=True,
            storeSupported=True
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="Dataset (NetCDF)",
            minOccurs=1,
            maxOccurs=1000,
            maxmegabites=10000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.output=self.addComplexOutput(
            identifier="output",
            title="CF Checker Report",
            abstract="",
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        self.status.set("starting cfchecker ...", 0)

        # TODO: iterate input files ... run parallel 
        # TODO: generate html report with links to cfchecker output ...
        outfile = 'out.txt'
        self.output.setValue( outfile )
        nc_files = self.getInputValues(identifier='dataset')
        count = 0
        max_count = len(nc_files)
        step = 100.0 / max_count
        for nc_file in nc_files:
            cf_report = cf_check(nc_file)
            with open(outfile, 'a') as fp:
                fp.write(cf_report)
                count = count + 1
                self.status.set("cfchecker: %d/%d" % (count, max_count), int(count*step))
        self.status.set("cfchecker: done", 100)


