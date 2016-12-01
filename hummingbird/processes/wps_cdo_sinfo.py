"""
Processes with cdo commands
"""
from cdo import Cdo
cdo_version = Cdo().version()

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format, FORMATS
from pywps.app.Common import Metadata

import logging
LOGGER = logging.getLogger("PYWPS")


class CDOInfo(Process):
    """This process calls cdo sinfo on netcdf file"""
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'NetCDF File',
                         abstract='You may provide a URL or upload a NetCDF file.',
                         metadata=[Metadata('Info')],
                         min_occurs=1,
                         max_occurs=100,
                         supported_formats=[Format('application/x-netcdf')]),
        ]
        outputs = [
            ComplexOutput('output', 'CDO sinfo result',
                          abstract='CDO sinfo result document.',
                          as_reference=True,
                          supported_formats=[Format('text/plain')]),
        ]

        super(CDOInfo, self).__init__(
            self._handler,
            identifier="cdo_sinfo",
            title="CDO sinfo",
            abstract="Apply CDO sinfo on NetCDF file and return document with metadata information.",
            version=cdo_version,
            metadata=[
                Metadata('Birdhouse', 'http://bird-house.github.io/'),
                Metadata('User Guide', 'http://birdhouse-hummingbird.readthedocs.io/en/latest/'),
                Metadata('CDO Homepage', 'https://code.zmaw.de/projects/cdo'),
                Metadata('CDO Documentation', 'https://code.zmaw.de/projects/cdo/embedded/index.html'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        datasets = [dataset.file for dataset in request.inputs['dataset']]

        cdo = Cdo()

        outfile = 'out.txt'
        with open(outfile, 'w') as fp:
            response.outputs['output'].file = outfile
            for ds in datasets:
                sinfo = cdo.sinfo(input=[ds], output=outfile)
                for line in sinfo:
                    fp.write(line + '\n')
                fp.write('\n\n')
        response.update_status("cdo sinfo done", 100)
        return response
