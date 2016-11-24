"""
Processes with cdo ensemble opertions
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


class Ensembles(Process):

    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'NetCDF File',
                         abstract='You may provide a URL or upload a NetCDF file.',
                         metadata=[Metadata('Info')],
                         min_occurs=1,
                         max_occurs=100,
                         supported_formats=[Format('application/x-netcdf')]),
            LiteralInput('operator', 'Ensemble command',
                         data_type='string',
                         abstract="Choose a CDO Operator",
                         min_occurs=1,
                         max_occurs=1,
                         default='ensmean',
                         allowed_values=['ensmin', 'ensmax', 'enssum', 'ensmean',
                                         'ensavg', 'ensvar', 'ensstd', 'enspctl']),
        ]

        outputs = [
            ComplexOutput('output', 'NetCDF Output',
                          abstract="CDO ensembles result.",
                          as_reference=True,
                          supported_formats=[Format('application/x-netcdf')]),
        ]

        super(Ensembles, self).__init__(
            self._handler,
            identifier="ensembles",
            title="CDO Ensembles Operations",
            abstract="Calling cdo to calculate ensembles operations.",
            version=cdo_version,
            metadata=[
                Metadata('Birdhouse', 'http://bird-house.github.io/'),
                Metadata('User Guide', 'http://birdhouse-hummingbird.readthedocs.io/en/latest/'),
                Metadata('CDO', 'https://code.zmaw.de/projects/cdo'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        datasets = [dataset.file for dataset in request.inputs['dataset']]
        operator = request.inputs['operator'][0].data

        cdo = Cdo()
        cdo_op = getattr(cdo, operator)

        outfile = 'out.nc'
        cdo_op(input=datasets, output=outfile)

        response.outputs['output'].file = outfile
        response.update_status("cdo ensembles done", 100)
        return response
