import os
from compliance_checker.runner import ComplianceCheckerCheckSuite
from compliance_checker.runner import ComplianceChecker as cc

from malleefowl.process import WPSProcess

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

import sys
from contextlib import contextmanager

@contextmanager
def stdout_redirected(new_stdout):
    """
    http://stackoverflow.com/questions/4675728/redirect-stdout-to-a-file-in-python
    """
    save_stdout = sys.stdout
    sys.stdout = new_stdout
    try:
        yield None
    finally:
        sys.stdout = save_stdout

class CFCheckerProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "cchecker",
            title = "IOOS Compliance Checker",
            version = "0.1",
            abstract="The IOOS Compliance Checker is a Python tool to check local/remote datasets against a variety of compliance standards."
            )

        self.resource = self.addComplexInput(
            identifier="resource",
            title="NetCDF File",
            abstract="NetCDF File",
            minOccurs=1,
            maxOccurs=1000,
            maxmegabites=10000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.test = self.addLiteralInput(
            identifier="test",
            title="Test Suite",
            abstract="Select the Checks you want to perform. Default: cf (climate forecast conventions)",
            default="cf",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=["cf", "gliderdac", "acdd", "ioos"]
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Report",
            abstract="",
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting ...", 0)

        # TODO: iterate input files ... run parallel 
        # TODO: generate html report with links to cfchecker output ...
        outfile = self.mktempfile(suffix='.txt')
        self.output.setValue( outfile )
        nc_files = self.getInputValues(identifier='resource')
        count = 0
        max_count = len(nc_files)
        step = 100.0 / max_count

        cs = ComplianceCheckerCheckSuite()
        test=self.test.getValue()

        with open(outfile, "w") as f:
            for nc_file in nc_files:
                f.write("\n\n####################################################################################\n")
                f.write("checking: %s\n" % nc_file)
                with stdout_redirected(f):
                    dataset = cs.load_dataset(nc_file)
                    groups = cs.run(dataset, test)
                    cc.stdout_output(cs, groups, verbose=0, limit=-1)
                count = count + 1
                self.show_status("checks: %d/%d" % (count, max_count), int(count*step))
        self.show_status("done", 100)


        
