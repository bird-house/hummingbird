from compliance_checker.runner import ComplianceChecker, CheckSuite
from compliance_checker import __version__ as cchecker_version

from hummingbird.processing import ncdump, cmor_checker

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
                         abstract="Select the test you want to run."
                                  " Default: CF-1.6 (climate forecast conventions)",
                         min_occurs=1,
                         max_occurs=1,
                         default='CF-1.6',
                         allowed_values=['CF-1.6', 'CORDEX', 'CMIP5', 'CMIP6']),
            ComplexInput('dataset', 'NetCDF File',
                         abstract='Enter a URL pointing to a NetCDF file (optional)',
                         metadata=[Metadata('Info')],
                         min_occurs=0,
                         max_occurs=1,
                         supported_formats=[Format('application/x-netcdf')]),
            LiteralInput('dataset_opendap', 'Remote OpenDAP Data URL',
                         data_type='string',
                         abstract="Or provide a remote OpenDAP data URL,"
                                  " for example: http://my.opendap/thredds/dodsC/path/to/file.nc",
                         metadata=[
                             Metadata(
                                 'application/x-ogc-dods',
                                 'https://www.iana.org/assignments/media-types/media-types.xhtml')],
                         min_occurs=0,
                         max_occurs=1),
        ]
        outputs = [
            ComplexOutput('output', 'Test Report',
                          abstract='Compliance checker test report.',
                          as_reference=True,
                          supported_formats=[Format('text/plain'), Format('text/html')]),
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
            abstract="Spot Checker checks datasets (NetCDF, OpenDAP) against a variety of compliance standards."
                     " Available compliance standards are the Climate and Forecast conventions (CF)"
                     " and project specific rules for CMIP6 and CORDEX.",
            metadata=[
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
        checker = request.inputs['test'][0].data
        if 'dataset_opendap' in request.inputs:
            if checker in ['CORDEX', 'CMIP5']:
                raise NotImplementedError("OpenDAP is not supported by DKRZ Quality Checker.")
            dataset = request.inputs['dataset_opendap'][0].data
        elif 'dataset' in request.inputs:
            dataset = request.inputs['dataset'][0].file
        else:
            raise Exception("missing dataset to check.")

        with open("nc_dump.txt", 'w') as fp:
            response.outputs['ncdump'].file = fp.name
            fp.writelines(ncdump(dataset))
            response.update_status('ncdump done.', 10)

        if 'CF' in checker:
            check_suite = CheckSuite()
            check_suite.load_all_available_checkers()

            with open("report.html", 'w') as fp:
                response.update_status("cfchecker ...", 20)
                response.outputs['output'].file = fp.name
                return_value, errors = ComplianceChecker.run_checker(
                    dataset,
                    checker_names=['cf'],
                    verbose=True,
                    criteria="normal",
                    output_filename=fp.name,
                    output_format="html")
        elif 'CMIP6' in checker:
            with open("cmip6-cmor.txt", 'w') as fp:
                response.outputs['output'].file = fp.name
                response.update_status("cmip6 checker ...", 20)
                cmor_checker(dataset, cmip6_table='CMIP6_CV', output_filename=fp.name)
        else:
            response.update_status("qa checker ...", 20)
            from hummingbird.processing import hdh_qa_checker
            logfile, _ = hdh_qa_checker(dataset, project=request.inputs['test'][0].data)
            response.outputs['output'].file = logfile

        response.update_status('spotchecker done.', 100)
        return response
