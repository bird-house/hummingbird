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
            abstract="The Spot Checker is a Python tool to\
             check local/remote datasets against a variety of\
             compliance standards. Each compliance standard is executed\
             by a Check Suite, which functions similar to a\
             Python standard Unit Test.\
             A Check Suite runs one or more checks against a dataset,\
             returning a list of Results which are then aggregated\
             into a summary.\
             Available compliance standards are the Climate and Forecast conventions (CF)\
             and project specific rules for CMIP6 and CORDEX.",
            metadata=[
                {'title': "User Guide",
                 'href': "http://birdhouse-hummingbird.readthedocs.io/en/latest/"},
                {'title': "CF Conventions",
                 'href': "http://cfconventions.org/"},
                {'title': "IOOS Compliance Online Checker",
                 'href': "http://data.ioos.us/compliance/index.html"}],
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
            abstract="You may provide a URL or upload a NetCDF file. (Max Size: 250MB)",
            minOccurs=0,
            maxOccurs=1,
            maxmegabites=250,
            formats=[{"mimeType": "application/x-netcdf"}],
        )

        self.dataset_opendap = self.addLiteralInput(
            identifier="dataset_opendap",
            title="Or provide a  remote OpenDAP Data URL",
            abstract="For example: http://my.opendap/thredds/dodsC/path/to/file.nc",
            type=type(''),
            minOccurs=0,
            maxOccurs=1,
        )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Test Report",
            abstract="Compliance checker test report.",
            formats=[{"mimeType": "text/html"}],
            asReference=True,
        )

        self.ncdump = self.addComplexOutput(
            identifier="ncdump",
            title="NetCDF Dump",
            abstract="ncdump of header of checked dataset.",
            formats=[{"mimeType": "text/plain"}],
            asReference=True,
        )

    def execute(self):
        # TODO: fix hummingbird import
        from hummingbird.processing import ncdump

        if self.getInputValue(identifier='dataset_opendap'):
            dataset = self.getInputValue(identifier='dataset_opendap')
        else:
            dataset = self.getInputValue(identifier='dataset')
        checkers = self.getInputValues(identifier='test')

        check_suite = CheckSuite()
        check_suite.load_all_available_checkers()

        with open("report.html", 'w') as fp:
            self.status.set("running cfchecker", 20)
            self.output.setValue(fp.name)
            return_value, errors = ComplianceChecker.run_checker(
                dataset,
                checker_names=checkers,
                verbose=True,
                criteria="normal",
                output_filename=fp.name,
                output_format="html")

        with open("nc_dump.txt", 'w') as fp:
            self.status.set("running ncdump", 80)
            self.ncdump.setValue(fp.name)
            fp.writelines(ncdump(dataset))

        self.status.set("compliance checker finshed.", 100)
