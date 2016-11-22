import os
import tarfile

from compliance_checker.runner import ComplianceChecker, CheckSuite
from compliance_checker import __version__ as cchecker_version

from pywps.Process import WPSProcess

import logging
logger = logging.getLogger(__name__)


class SpotCheckerProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="spotchecker",
            title="Spot Checker",
            version="0.1.0",
            abstract="Compliance checker for CF etc",
            metadata=[
                {'title': "IOOS Compliance Online Checker",
                 'href': 'http://data.ioos.us/compliance/index.html'}],
            statusSupported=True,
            storeSupported=True
        )

        self.test = self.addLiteralInput(
            identifier="test",
            title="Test Suite",
            abstract="Select the test you want to run.\
             Default: cf (climate forecast conventions)",
            default="cf",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['cf']
        )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="URL to your NetCDF File",
            abstract="You may provide a URL or upload a NetCDF file. (Max Size: 100MB)",
            minOccurs=1,
            maxOccurs=1,
            maxmegabites=100,
            formats=[{"mimeType": "application/x-netcdf"}],
        )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Test Report",
            abstract="Compliance checker test report.",
            formats=[{"mimeType": "text/html"}],
            asReference=True,
        )

    def execute(self):
        # TODO: iterate input files ... run parallel
        # TODO: generate html report with links to cfchecker output ...
        dataset = self.getInputValue(identifier='dataset')
        checkers = self.getInputValues(identifier='test')
        output_format = self.getInputValue(identifier='format')

        check_suite = CheckSuite()
        check_suite.load_all_available_checkers()

        outfile = "report.html"
        self.output.setValue(outfile)

        with open(outfile, 'w') as fp:
            return_value, errors = ComplianceChecker.run_checker(
                dataset,
                checker_names=checkers,
                verbose=True,
                criteria="normal",
                output_filename=outfile,
                output_format="html")

        self.status.set("compliance checker finshed.", 100)
