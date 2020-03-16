import os

from compliance_checker.runner import ComplianceChecker, CheckSuite
from compliance_checker import __version__ as cchecker_version

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

import logging
LOGGER = logging.getLogger("PYWPS")


class CChecker(Process):
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Dataset',
                         abstract='You may provide a URL or upload a NetCDF/CDL file.',
                         min_occurs=0,
                         max_occurs=1,
                         supported_formats=[FORMATS.NETCDF, FORMATS.TEXT]),
            ComplexInput('dataset_opendap', 'Remote OpenDAP Data URL',
                         abstract="Or provide a remote OpenDAP data URL,"
                                  " for example:"
                                  " http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2.dailyavgs/surface/mslp.2016.nc",  # noqa
                         min_occurs=0,
                         max_occurs=1,
                         supported_formats=[FORMATS.DODS]),
            LiteralInput('test', 'Test Suite',
                         data_type='string',
                         abstract="Select the test you want to run."
                                  " Default: cf (climate forecast conventions)",
                         min_occurs=1,
                         max_occurs=1,
                         default='cf',
                         allowed_values=['cf', 'cf:1.7', 'cf:1.6', 'cmip6_cv']),
            LiteralInput('criteria', 'Criteria',
                         data_type='string',
                         abstract="Define the criteria for the checks.  Either Strict, Normal or Lenient."
                                  " Defaults to Normal.",
                         min_occurs=1,
                         max_occurs=1,
                         default='normal',
                         allowed_values=['strict', 'normal', 'lenient']),
            LiteralInput('format', 'Output Format',
                         data_type='string',
                         abstract="The format of the check reporst. Either text, json or html. Defaults to html.",
                         min_occurs=1,
                         max_occurs=1,
                         default='html',
                         allowed_values=['text', 'json', 'html']),
        ]

        outputs = [
            ComplexOutput('output', 'Check Report',
                          abstract="Report of check result.",
                          as_reference=True,
                          supported_formats=[Format('text/html')]),
        ]

        super(CChecker, self).__init__(
            self._handler,
            identifier="cchecker",
            title="IOOS Compliance Checker",
            version=cchecker_version,
            abstract="Runs the IOOS Compliance Checker tool to"
                     " check datasets against compliance standards.",
            metadata=[
                Metadata('CF Conventions', 'http://cfconventions.org/'),
                Metadata('IOOS Compliance Online Checker', 'http://data.ioos.us/compliance/index.html'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        dataset = None
        if 'dataset_opendap' in request.inputs:
            dataset = request.inputs['dataset_opendap'][0].url
            LOGGER.debug("opendap dataset url: {}".format(dataset))
        elif 'dataset' in request.inputs:
            dataset = request.inputs['dataset'][0].file
            LOGGER.debug("opendap dataset file: {}".format(dataset))

        if not dataset:
            raise ProcessError("You need to provide a Dataset.")

        output_format = request.inputs['format'][0].data

        check_suite = CheckSuite()
        check_suite.load_all_available_checkers()
        if not request.inputs['test'][0].data in check_suite.checkers:
            raise ProcessError("Test {} is not available.".format(request.inputs['test'][0].data))

        output_file = os.path.join(
            self.workdir,
            "check_report.{}".format(output_format))

        LOGGER.info("checking dataset {}".format(dataset))
        ComplianceChecker.run_checker(
            dataset,
            checker_names=[checker.data for checker in request.inputs['test']],
            verbose=True,
            criteria=request.inputs['criteria'][0].data,
            output_filename=output_file,
            output_format=output_format)
        response.outputs['output'].file = output_file
        response.update_status("compliance checker finshed.", 100)
        return response
