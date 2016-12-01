from compliance_checker.runner import ComplianceChecker, CheckSuite
from compliance_checker import __version__ as cchecker_version

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format, FORMATS
from pywps.app.Common import Metadata

import logging
LOGGER = logging.getLogger("PYWPS")


class SpotChecker(Process):
    def __init__(self):
        inputs = [
            LiteralInput('test', 'Test Suite',
                         data_type='string',
                         abstract="Select the test you want to run.\
                          Default: cf (climate forecast conventions)",
                         min_occurs=1,
                         max_occurs=1,
                         default='cf',
                         allowed_values=['cf']),
            ComplexInput('dataset', 'NetCDF File',
                         abstract='Enter a URL pointing to a NetCDF file (optional)',
                         metadata=[Metadata('Info')],
                         min_occurs=0,
                         max_occurs=1,
                         supported_formats=[Format('application/x-netcdf')]),
            LiteralInput('dataset_opendap', 'Remote OpenDAP Data URL',
                         data_type='string',
                         abstract="Or provide a remote OpenDAP data URL,\
                          for example: http://my.opendap/thredds/dodsC/path/to/file.nc",
                         min_occurs=0,
                         max_occurs=1),
        ]
        outputs = [
            ComplexOutput('output', 'Test Report',
                          abstract='Compliance checker test report.',
                          as_reference=True,
                          supported_formats=[Format('text/plain')]),
            ComplexOutput('ncdump', 'ncdump of metadata',
                          abstract='ncdump of header of checked dataset.',
                          as_reference=True,
                          supported_formats=[Format('text/plain')]),
        ]

        super(SpotChecker, self).__init__(
            self._handler,
            identifier="spotchecker",
            title="Spot Checker",
            version="0.2.0",
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
                Metadata('Birdhouse', 'http://bird-house.github.io/'),
                Metadata('User Guide', 'http://birdhouse-hummingbird.readthedocs.io/en/latest/'),
                Metadata('CF Conventions', 'http://cfconventions.org/'),
                Metadata('IOOS Compliance Online Checker', 'http://data.ioos.us/compliance/index.html'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        from hummingbird.processing import ncdump

        if 'dataset_opendap' in request.inputs:
            dataset = request.inputs['dataset_opendap'][0].data
        elif 'dataset' in request.inputs:
            dataset = request.inputs['dataset'][0].file
        else:
            raise Exception("missing dataset to check.")
        checkers = [checker.data for checker in request.inputs['test']]

        check_suite = CheckSuite()
        check_suite.load_all_available_checkers()

        with open("report.html", 'w') as fp:
            response.update_status("running cfchecker", 20)
            response.outputs['output'].output_format = FORMATS.TEXT
            response.outputs['output'].file = fp.name
            return_value, errors = ComplianceChecker.run_checker(
                dataset,
                checker_names=checkers,
                verbose=True,
                criteria="normal",
                output_filename=fp.name,
                output_format="html")

        with open("nc_dump.txt", 'w') as fp:
            response.update_status("running ncdump", 80)
            response.outputs['ncdump'].output_format = FORMATS.TEXT
            response.outputs['ncdump'].file = fp.name
            fp.writelines(ncdump(dataset))
        response.update_status('compliance checker finshed...', 100)
        return response
