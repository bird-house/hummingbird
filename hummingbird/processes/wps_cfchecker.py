import os
from subprocess import check_output, CalledProcessError

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import FORMATS
from pywps.app.Common import Metadata

import logging
LOGGER = logging.getLogger("PYWPS")


def cf_check(nc_file, version):
    # TODO: avoid downloading of cf table for each check (see pypi page)
    LOGGER.debug("checking %s", os.path.basename(nc_file))
    if not nc_file.endswith(".nc"):
        new_name = nc_file + ".nc"
        os.rename(nc_file, new_name)
        nc_file = new_name
    cmd = ["cfchecks", "--version", version, nc_file]
    try:
        cf_report = check_output(cmd)
    except CalledProcessError as err:
        LOGGER.warn("cfchecks failed!")
        cf_report = err.output
    return cf_report


class CFChecker(Process):
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Dataset',
                         abstract='You may provide a URL or upload a NetCDF/CDL file.',
                         min_occurs=0,
                         max_occurs=100,
                         supported_formats=[FORMATS.NETCDF, FORMATS.TEXT]),
            LiteralInput('cf_version', 'Check against CF version',
                         data_type='string',
                         abstract="Version of CF conventions that the NetCDF file should be check against."
                                  " Use auto to auto-detect the CF version.",
                         min_occurs=1,
                         max_occurs=1,
                         default='auto',
                         allowed_values=["auto", "1.7", "1.6", "1.5", "1.4", "1.3", "1.2", "1.1", "1.0"]),
        ]
        outputs = [
            ComplexOutput('output', 'CF Checker Report',
                          abstract="Summary of the CF compliance check",
                          as_reference=True,
                          supported_formats=[FORMATS.TEXT]),
        ]

        super(CFChecker, self).__init__(
            self._handler,
            identifier="cfchecker",
            title="CF Checker by CEDA",
            version="4.0.0",
            abstract="The NetCDF Climate Forecast Conventions compliance checker by CEDA."
                     " This process allows you to run the compliance checker"
                     " to check that the contents of a NetCDF file comply"
                     " with the Climate and Forecasts (CF) Metadata Convention.",
            metadata=[
                Metadata('CF Conventions', 'http://cfconventions.org/'),
                Metadata('Online Compliance Checker', 'http://cfconventions.org/compliance-checker.html'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        datasets = []
        if 'dataset' in request.inputs:
            for dataset in request.inputs['dataset']:
                datasets.append(dataset.file)

        output_file = os.path.join(self.workdir, 'cfchecker_output.txt')
        for dataset in datasets:
            cf_report = cf_check(dataset, version=request.inputs['cf_version'][0].data)
            with open(output_file, 'a') as fp:
                fp.write("{}\n\n".format(cf_report.decode('UTF-8', 'ignore')))
        response.outputs['output'].file = output_file
        response.update_status("cfchecker done.", 100)
        return response
