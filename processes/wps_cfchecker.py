import os
from subprocess import check_output, CalledProcessError

from pywps.Process import WPSProcess
from malleefowl.process import show_status, getInputValues, mktempfile

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

def cf_check(nc_file, version):
    logger.debug("start cf_check: nc_file=%s, version=%s", nc_file, version)
    # TODO: maybe use local file path
    if not nc_file.endswith(".nc"):
        new_name = nc_file + ".nc"
        from os import rename
        rename(nc_file, new_name)
        nc_file = new_name
    cmd = ["cfchecks", "--version", version, nc_file]
    try:
        cf_report = check_output(cmd)
    except CalledProcessError as err:
        logger.exception("cfchecks failed!")
        cf_report = err.output
    return cf_report

class CFCheckerProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "cfchecker",
            title = "CF Checker",
            version = "2.0.9-2",
            abstract="The cfchecker checks NetCDF files for compliance to the CF standard.",
            statusSupported=True,
            storeSupported=True
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="NetCDF File",
            minOccurs=1,
            maxOccurs=1000,
            maxmegabites=10000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.cf_version = self.addLiteralInput(
            identifier="cf_version",
            title="CF version",
            abstract="CF version to check against, use auto to auto-detect the file version.",
            default="auto",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=["auto", "1.6", "1.5", "1.4", "1.3", "1.2", "1.1"]
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="CF Checker Report",
            abstract="",
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        show_status(self, "starting cfchecker ...", 0)

        # TODO: iterate input files ... run parallel 
        # TODO: generate html report with links to cfchecker output ...
        outfile = mktempfile(suffix='.txt')
        self.output.setValue( outfile )
        nc_files = getInputValues(self, identifier='dataset')
        count = 0
        max_count = len(nc_files)
        step = 100.0 / max_count
        for nc_file in nc_files:
            cf_report = cf_check(nc_file, version=self.cf_version.getValue())
            with open(outfile, 'a') as fp:
                fp.write(cf_report)
                count = count + 1
                show_status(self, "cfchecker: %d/%d" % (count, max_count), int(count*step))
        show_status(self, "cfchecker: done", 100)


        
