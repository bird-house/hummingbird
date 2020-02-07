import os
from compliance_checker.runner import ComplianceChecker, CheckSuite

from hummingbird.processing import ncdump, cmor_checker

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format, FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

import logging
LOGGER = logging.getLogger("PYWPS")


class SpotChecker(Process):
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Upload your NetCDF file here',
                         abstract='or enter a URL pointing to a NetCDF file.',
                         metadata=[Metadata('Info')],
                         min_occurs=0,
                         max_occurs=1,
                         supported_formats=[FORMATS.NETCDF]),
            ComplexInput('dataset_opendap', 'Remote OpenDAP Data URL',
                         abstract="Or provide a remote OpenDAP data URL,"
                                  " for example:"
                                  " http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2.dailyavgs/surface/mslp.2016.nc",  # noqa
                         min_occurs=0,
                         max_occurs=1,
                         supported_formats=[FORMATS.DODS]),
            LiteralInput('test', 'Select the test you want to run.',
                         data_type='string',
                         abstract="CF-1.6=Climate and Forecast Conventions (CF)",
                         min_occurs=1,
                         max_occurs=1,
                         default='CF-1.6',
                         allowed_values=['CF-1.6', ]),  # , 'CORDEX', 'CMIP5', 'CMIP6']),
        ]
        outputs = [
            ComplexOutput('output', 'Test Report',
                          abstract='Compliance checker test report.',
                          as_reference=True,
                          supported_formats=[Format('text/html'), FORMATS.TEXT]),
            ComplexOutput('ncdump', 'ncdump of metadata',
                          abstract='ncdump of header of checked dataset.',
                          as_reference=True,
                          supported_formats=[FORMATS.TEXT]),
        ]

        super(SpotChecker, self).__init__(
            self._handler,
            identifier="spotchecker",
            title="Spot Checker",
            version="0.3.1",
            abstract="Checks a single uploaded or remote dataset against a variety of compliance standards."
                     " The dataset is either in the NetCDF format or a remote OpenDAP resource."
                     " Available compliance standards are the Climate and Forecast conventions (CF)"
                     " and project specific rules for CMIP6 and CORDEX.",
            metadata=[
                Metadata('User Guide', 'http://birdhouse-hummingbird.readthedocs.io/en/latest/processes.html#spotchecker'),  # noqa
                Metadata('CF Conventions', 'http://cfconventions.org/'),
                Metadata('IOOS Compliance Online Checker', 'http://data.ioos.us/compliance/index.html'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        if 'dataset_opendap' in request.inputs:
            dataset = request.inputs['dataset_opendap'][0].url
        elif 'dataset' in request.inputs:
            dataset = request.inputs['dataset'][0].file
        else:
            raise ProcessError("You need to provide a Dataset.")

        checker = request.inputs['test'][0].data

        with open(os.path.join(self.workdir, "nc_dump.txt"), 'w') as fp:
            response.outputs['ncdump'].file = fp.name
            fp.writelines(ncdump(dataset))
            response.update_status('ncdump done.', 10)

        if 'CF' in checker:
            check_suite = CheckSuite()
            check_suite.load_all_available_checkers()

            with open(os.path.join(self.workdir, "report.html"), 'w') as fp:
                response.update_status("cfchecker ...", 20)
                response.outputs['output'].file = fp.name
                ComplianceChecker.run_checker(
                    dataset,
                    checker_names=['cf'],
                    verbose=True,
                    criteria="normal",
                    output_filename=fp.name,
                    output_format="html")
        elif 'CMIP6' in checker:
            with open(os.path.join(self.workdir, "cmip6-cmor.txt"), 'w') as fp:
                response.outputs['output'].file = fp.name
                response.update_status("cmip6 checker ...", 20)
                cmor_checker(dataset, output_filename=fp.name)
        else:
            response.update_status("qa checker ...", 20)
            from hummingbird.processing import hdh_qa_checker
            logfile, _ = hdh_qa_checker(dataset, project=request.inputs['test'][0].data)
            response.outputs['output'].file = logfile

        response.update_status('spotchecker done.', 100)
        return response
