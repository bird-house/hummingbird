import os
from subprocess import check_output, CalledProcessError

from pywps.Process import WPSProcess

import logging

def cf_check(nc_file, version):
    # TODO: maybe use local file path
    # TODO: avoid downloading of cf table for each check (see pypi page)
    if not nc_file.endswith(".nc"):
        new_name = nc_file + ".nc"
        os.rename(nc_file, new_name)
        nc_file = new_name
    cmd = ["cfchecks", "--version", version, nc_file]
    try:
        cf_report = check_output(cmd)
    except CalledProcessError as err:
        logging.exception("cfchecks failed!")
        cf_report = err.output
    return cf_report

class CFCheckerProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "cfchecker",
            title = "CF Checker by BADC",
            version = "2.0.9-0",
            abstract="The NetCDF Climate Forcast Conventions compliance checker.",
            metadata= [ {"title": "Homepage" , "href": "https://pypi.python.org/pypi/cfchecker"} ],
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
        # TODO: iterate input files ... run parallel 
        # TODO: generate html report with links to cfchecker output ...
        outfile = 'output.txt'
        self.output.setValue( outfile )
        nc_files = self.getInputValues(identifier='dataset')
        count = 0
        max_count = len(nc_files)
        step = 100.0 / max_count
        for nc_file in nc_files:
            cf_report = cf_check(nc_file, version=self.cf_version.getValue())
            with open(outfile, 'a') as fp:
                fp.write(cf_report)
                count = count + 1
                self.status.set("cfchecker: %d/%d" % (count, max_count), int(count*step))
        self.status.set("cfchecker: done", 100)


        
