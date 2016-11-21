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

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="URL to your NetCDF File",
            abstract="You may provide a URL or upload a NetCDF file.",
            minOccurs=1,
            maxOccurs=1,
            maxmegabites=1000,
            formats=[{"mimeType": "application/x-netcdf"}],
        )

        self.test = self.addLiteralInput(
            identifier="test",
            title="Test Suite",
            abstract="Select the Checks you want to perform.\
             Default: cf (climate forecast conventions)",
            default="cf",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['cf']
        )

        self.output_format = self.addLiteralInput(
            identifier="format",
            title="Output Format",
            abstract="The format of the check reporst. Either text, json or html. Defaults to html.",
            type=type(''),
            default="html",
            minOccurs=1,
            maxOccurs=1,
            allowedValues=["text", "json", "html"]
        )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Check Report",
            abstract="Report of check result.",
            formats=[{"mimeType": "text/html"}, {"mimeType": "plain/text"}],
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

        outfile = "report.{0}".format(output_format)
        self.output.setValue(outfile)

        with open(outfile, 'w') as fp:
            return_value, errors = ComplianceChecker.run_checker(
                dataset,
                checker_names=checkers,
                verbose=True,
                criteria="normal",
                output_filename=outfile,
                output_format=output_format)

        self.status.set("compliance checker finshed.", 100)
