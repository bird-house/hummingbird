import os
from compliance_checker.runner import ComplianceCheckerCheckSuite, ComplianceChecker

from pywps.Process import WPSProcess
from malleefowl.process import show_status, getInputValues, mktempfile

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

import sys
from contextlib import contextmanager

check_suite = ComplianceCheckerCheckSuite()

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
            identifier = "ioos_cchecker",
            title = "IOOS Compliance Checker",
            version = "1.1.1-4",
            abstract="The IOOS Compliance Checker is a Python tool to check local/remote datasets against a variety of compliance standards.",
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

        self.test = self.addLiteralInput(
            identifier="test",
            title="Test Suite",
            abstract="Select the Checks you want to perform. Default: cf (climate forecast conventions)",
            default="cf",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=check_suite.checkers.keys()
            )

        self.criteria = self.addLiteralInput(
            identifier="criteria",
            title="Criteria",
            abstract="Define the criteria for the checks.  Either Strict, Normal, or Lenient.  Defaults to Normal.",
            type=type(''),
            default="normal",
            minOccurs=1,
            maxOccurs=1,
            allowedValues=["strict", "normal", "lenient"]
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Report",
            abstract="",
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        show_status(self, "starting ...", 0)

        # TODO: iterate input files ... run parallel 
        # TODO: generate html report with links to cfchecker output ...
        outfile = mktempfile(suffix='.txt')
        self.output.setValue( outfile )
        datasets = getInputValues(self, identifier='dataset')
        checker_names = getInputValues(self, identifier='test')
        
        count = 0
        max_count = len(datasets)
        step = 100.0 / max_count

        with open(outfile, "w") as f:
            for ds in datasets:
                f.write("\n\n####################################################################################\n")
                f.write("checking: %s\n" % ds)
                with stdout_redirected(f):
                    ComplianceChecker.run_checker(
                        ds,
                        checker_names=checker_names,
                        verbose=0,
                        criteria=self.criteria.getValue())
                count = count + 1
                show_status(self, "checks: %d/%d" % (count, max_count), int(count*step))
        show_status(self, "done", 100)


        
