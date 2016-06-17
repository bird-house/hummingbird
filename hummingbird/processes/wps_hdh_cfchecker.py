import os
import shutil
from subprocess import check_output, CalledProcessError, STDOUT

from pywps.Process import WPSProcess
import logging
logger = logging.getLogger(__name__)

def cf_check(filename):
    # TODO: maybe use local file path
    if not filename.endswith(".nc"):
        new_name = filename + ".nc"
        from os import rename
        rename(filename, new_name)
        filename = new_name
    filename = os.path.abspath(filename)
    cmd = ["dkrz-cf-checker", filename]
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
            title="CF Checker by DKRZ",
            version="0.5.12",
            abstract="cfchecker checks NetCDF files for compliance to the CF standard.",
            metadata= [ {"title": "Documentation" , "href": "http://qa-dkrz.readthedocs.io/en/latest/"} ],
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


