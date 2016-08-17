import os
import sys
from contextlib import contextmanager
from compliance_checker.runner import ComplianceChecker, CheckSuite
from compliance_checker import __version__ as cchecker_version

from pywps.Process import WPSProcess

import logging
logger = logging.getLogger(__name__)

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
            version = cchecker_version,
            abstract="The IOOS Compliance Checker is a Python tool to check local/remote datasets against a variety of compliance standards. Each compliance standard is executed by a Check Suite, which functions similar to a Python standard Unit Test. A Check Suite runs one or more checks against a dataset, returning a list of Results which are then aggregated into a summary. Development and maintenance for the compliance checker is done by the Integrated Ocean Observing System (IOOS).",
            metadata = [
                {'title': "Compliance Checker on GitHub", 'href': "https://github.com/ioos/compliance-checker"},
                {'title': "IOOS", 'href': 'https://ioos.noaa.gov/'},
                {'title': "IOOS Compliance Online Checker", 'href': 'http://data.ioos.us/compliance/index.html'}],
            statusSupported=True,
            storeSupported=True
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="URL to your NetCDF File",
            abstract="You may provide a URL or upload a NetCDF file.",
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
            allowedValues=['cf', 'ioos', 'acdd']
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
            title="Results Summary",
            abstract="Summary report of all check results.",
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        # TODO: iterate input files ... run parallel 
        # TODO: generate html report with links to cfchecker output ...
        outfile = 'out.txt'
        self.output.setValue( outfile )
        datasets = self.getInputValues(identifier='dataset')
        checkers = self.getInputValues(identifier='test')

        count = 0
        max_count = len(datasets)
        step = 100.0 / max_count

        check_suite = CheckSuite()
        check_suite.load_all_available_checkers()

        return_values = []
        had_errors = []
      
        with open(outfile, "w") as f:
            for ds in datasets:
                f.write("\n\n####################################################################################\n")
                f.write("Running Compliance Checker on dataset: {}\n".format(ds))
                with stdout_redirected(f):
                    return_value, errors = ComplianceChecker.run_checker(
                        ds,
                        checker_names=checkers,
                        verbose=0,
                        criteria=self.criteria.getValue(),
                        output_filename='-',
                        output_format='text')
                    return_values.append(return_value)
                    had_errors.append(errors)
                count = count + 1
                self.status.set("checks: %d/%d" % (count, max_count), int(count*step))

        if any(had_errors):
            msg = "complince checker finshed with errors."
            logger.warning(msg)
            self.status.set(msg, 100)
        elif all(return_values):
            self.status.set("compliance checker finshed successfully", 100)
        else:
            msg = "complince checker finshed with errors."
            logger.warning(msg)
            self.status.set(msg, 100)


        
