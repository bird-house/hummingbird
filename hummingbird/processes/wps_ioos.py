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

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="URL to your NetCDF File",
            abstract="You may provide a URL or upload a NetCDF file.",
            minOccurs=0,
            maxOccurs=100,
            maxmegabites=1024,
            formats=[{"mimeType": "application/x-netcdf"}],
        )

        self.dataset_opendap = self.addLiteralInput(
            identifier="dataset_opendap",
            title="Remote OpenDAP Data URL",
            abstract="Or provide a remote OpenDAP data URL,\
             for example: http://my.opendap/thredds/dodsC/path/to/file.nc",
            type=type(''),
            minOccurs=0,
            maxOccurs=100,
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
            title="Summary",
            abstract="Summary report of check results.",
            formats=[{"mimeType": "plain/text"}],
            asReference=True,
        )

        self.output_report = self.addComplexOutput(
            identifier="report",
            title="Check Report",
            abstract="Report of check result.",
            formats=[{"mimeType": "text/html"}, {"mimeType": "plain/text"}],
            asReference=True,
        )

        self.output_tar = self.addComplexOutput(
            identifier="report_tar",
            title="Reports as tarfile",
            abstract="Report of check result for each file as tarfile.",
            formats=[{"mimeType": "application/x-tar"}],
            asReference=True,
        )

    def execute(self):
        # TODO: iterate input files ... run parallel
        # TODO: generate html report with links to cfchecker output ...
        datasets = self.getInputValues(identifier='dataset')
        # append opendap urls
        datasets.extend(self.getInputValues(identifier='dataset_opendap'))
        output_format = self.getInputValue(identifier='format')

        count = 0
        max_count = len(datasets)
        step = 100.0 / max_count

        check_suite = CheckSuite()
        check_suite.load_all_available_checkers()

        # return_values = []
        # had_errors = []

        # output
        os.mkdir("report")
        self.output_report.setValue("report/0.{0}".format(output_format))

        with open('report/summary.txt', 'w') as fp:
            self.output.setValue(fp.name)
            for ds in datasets:
                logger.info("checking dataset %s", ds)
                report_file = "report/{0}.{1}".format(count, output_format)
                return_value, errors = ComplianceChecker.run_checker(
                    ds,
                    checker_names=self.getInputValues(identifier='test'),
                    verbose=True,
                    criteria=self.criteria.getValue(),
                    output_filename=report_file,
                    output_format=output_format)
                if return_value is False:
                    logger.info("dataset %s with errors %s" % (ds, errors))
                    fp.write("{0}, FAIL, {1}\n".format(ds, report_file))
                else:
                    fp.write("{0}, PASS, {1}\n".format(ds, report_file))
                count = count + 1

                self.status.set("checks: %d/%d"
                                % (count, max_count), int(count * step))
        with tarfile.open("report.tar", "w") as tar:
            self.output_tar.setValue(fp.name)
            tar.add("report")

        self.status.set("compliance checker finshed.", 100)
