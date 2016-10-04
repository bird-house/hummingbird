import os
import tarfile

from compliance_checker.runner import ComplianceChecker, CheckSuite
from compliance_checker import __version__ as cchecker_version

from pywps.Process import WPSProcess

import logging
logger = logging.getLogger(__name__)


class CFCheckerProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="ioos_cchecker",
            title="IOOS Compliance Checker",
            version=cchecker_version,
            abstract="The IOOS Compliance Checker is a Python tool to\
             check local/remote datasets against a variety of\
             compliance standards. Each compliance standard is executed\
             by a Check Suite, which functions similar to a\
             Python standard Unit Test.\
             A Check Suite runs one or more checks against a dataset,\
             returning a list of Results which are then aggregated\
             into a summary. Development and maintenance for the compliance\
             checker is done by the Integrated Ocean Observing System (IOOS).",
            metadata=[
                {'title': "Compliance Checker on GitHub", 'href':
                 "https://github.com/ioos/compliance-checker"},
                {'title': "IOOS", 'href': 'https://ioos.noaa.gov/'},
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
            maxOccurs=1000,
            maxmegabites=10000,
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
            allowedValues=['cf', 'ioos', 'acdd']
            )

        self.criteria = self.addLiteralInput(
            identifier="criteria",
            title="Criteria",
            abstract="Define the criteria for the checks.  Either Strict, Normal or Lenient.  Defaults to Normal.",
            type=type(''),
            default="normal",
            minOccurs=1,
            maxOccurs=1,
            allowedValues=["strict", "normal", "lenient"]
            )

        # self.output_format = self.addLiteralInput(
        #     identifier="format",
        #     title="Output Format",
        #     abstract="The format of the check reporst. Either text, json or html. Defaults to json.",
        #     type=type(''),
        #     default="json",
        #     minOccurs=1,
        #     maxOccurs=1,
        #     allowedValues=["text", "json", "html"]
        #     )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Summary",
            abstract="Summary report of check results.",
            formats=[{"mimeType": "plain/text"}],
            asReference=True,
            )

        # self.output_text = self.addComplexOutput(
        #     identifier="text",
        #     title="Text Report",
        #     abstract="Text report of check results.",
        #     formats=[{"mimeType": "plain/text"}],
        #     asReference=True,
        #     )

        self.output_html = self.addComplexOutput(
            identifier="html",
            title="HTML Report",
            abstract="HTML Report of check result.",
            formats=[{"mimeType": "text/html"}],
            asReference=True,
            )

        self.output_html_tar = self.addComplexOutput(
            identifier="html_tar",
            title="HTML Reports as tarfile",
            abstract="HTML Report of check result for each file as tarfile.",
            formats=[{"mimeType": "application/x-tar"}],
            asReference=True,
            )

    def execute(self):
        # TODO: iterate input files ... run parallel
        # TODO: generate html report with links to cfchecker output ...
        datasets = self.getInputValues(identifier='dataset')
        checkers = self.getInputValues(identifier='test')

        count = 0
        max_count = len(datasets)
        step = 100.0 / max_count

        check_suite = CheckSuite()
        check_suite.load_all_available_checkers()

        return_values = []
        had_errors = []

        # output
        os.mkdir("report")
        outfile = 'report/summary.txt'
        self.output.setValue(outfile)
        self.output_html.setValue("report/0.html")
        self.output_html_tar.setValue("report.tar")
        #self.output_text.setValue("report/0.txt")

        with open(outfile, 'w') as fp:
            for ds in datasets:
                logger.info("checking dataset %s", ds)
                report_file = "report/{0}.html".format(count)
                return_value, errors = ComplianceChecker.run_checker(
                    ds,
                    checker_names=checkers,
                    verbose=True,
                    criteria=self.criteria.getValue(),
                    output_filename=report_file,
                    output_format='html')
                if return_value is False:
                    logger.info("dataset %s with errors %s" % (ds, errors))
                    fp.write("{0}, FAIL, {1}\n".format(ds, report_file))
                else:
                    fp.write("{0}, PASS, {1}\n".format(ds, report_file))
                count = count + 1

                self.status.set("checks: %d/%d"
                                % (count, max_count), int(count*step))
        with tarfile.open("report.tar", "w") as tar:
            tar.add("report")

        self.status.set("compliance checker finshed.", 100)
