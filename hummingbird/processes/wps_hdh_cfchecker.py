import os
import shutil
from subprocess import check_output, CalledProcessError, STDOUT

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format, FORMATS
from pywps.app.Common import Metadata

import logging
LOGGER = logging.getLogger("PYWPS")


def cf_check(filename, version="auto"):
    # TODO: maybe use local file path
    if not filename.endswith(".nc"):
        new_name = filename + ".nc"
        from os import rename
        rename(filename, new_name)
        filename = new_name
    filename = os.path.abspath(filename)
    cmd = ["dkrz-cf-checker", filename]
    if version != "auto":
        cmd.extend(['-C', version])
    try:
        output = check_output(cmd)
    except CalledProcessError as err:
        LOGGER.exception("cfchecks failed!")
        output = err.output
    return output


class HDHCFChecker(Process):
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'NetCDF File',
                         abstract='You may provide a URL or upload a NetCDF file.',
                         metadata=[Metadata('Info')],
                         min_occurs=1,
                         max_occurs=100,
                         supported_formats=[Format('application/x-netcdf')]),
            LiteralInput('cf_version', 'Check against CF version',
                         data_type='string',
                         abstract="Version of CF conventions that the NetCDF file should be check against.\
                          Use auto to auto-detect the CF version.",
                         min_occurs=1,
                         max_occurs=1,
                         default='auto',
                         allowed_values=["auto", "1.6", "1.5", "1.4"]),
        ]
        outputs = [
            ComplexOutput('output', 'CF Checker Report',
                          abstract="Summary of the CF compliance check",
                          as_reference=True,
                          supported_formats=[Format('text/plain')]),
        ]

        super(HDHCFChecker, self).__init__(
            self._handler,
            identifier="qa_cfchecker",
            title="CF Checker by DKRZ",
            version="0.5.17",
            abstract="The NetCDF Climate Forcast Conventions compliance checker by DKRZ.\
             This process allows you to run the compliance checker to check that the contents of a NetCDF file comply\
             with the Climate and Forecasts (CF) Metadata Convention.\
             The CF Conformance checker applies to conventions 1.4 -1.7draft.\
             Development and maintenance for the CF-checker is done by the German Climate Computing Centre (DKRZ).\
             If you have suggestions for improvement then please contact\
             Heinz-Dieter Hollweg at DKRZ (hollweg@dkrz.de).",
            metadata=[
                Metadata('Birdhouse', 'http://bird-house.github.io/'),
                Metadata('User Guide', 'http://birdhouse-hummingbird.readthedocs.io/en/latest/'),
                Metadata('CF Conventions', 'http://cfconventions.org/'),
                Metadata('CF Checker Documentation', 'http://qa-dkrz.readthedocs.io/en/latest/'),
                Metadata('Conda Package', 'http://anaconda.org/birdhouse/qa-dkrz'),
                Metadata('GitHub', 'https://github.com/IS-ENES-Data/QA-DKRZ'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        response.update_status("starting cfchecker ...", 0)

        # TODO: iterate input files ... run parallel
        # TODO: generate html report with links to cfchecker output ...
        datasets = [dataset.file for dataset in request.inputs['dataset']]

        max_count = len(datasets)
        step = 100.0 / max_count
        for idx, dataset in enumerate(datasets):
            cf_report = cf_check(dataset, version=request.inputs['cf_version'][0].data)
            with open('cfchecker_output.txt', 'a') as fp:
                response.outputs['output'].file = fp.name
                fp.write(cf_report)
                response.update_status("cfchecker: %d/%d" % (idx, max_count), int(idx * step))
        response.update_status("cfchecker done.", 100)
        return response
