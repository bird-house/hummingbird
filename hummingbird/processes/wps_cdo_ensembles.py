"""
Processes with cdo ensemble opertions
"""
import os.path
from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import FORMATS
from pywps.app.Common import Metadata

from hummingbird.processing import cdo_version, get_cdo

import logging
LOGGER = logging.getLogger("PYWPS")


class CDOEnsembles(Process):

    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Dataset',
                         abstract='You may provide a URL or upload a NetCDF file.',
                         min_occurs=0,
                         max_occurs=10,
                         supported_formats=[FORMATS.NETCDF]),
            ComplexInput('dataset_opendap', 'Remote OpenDAP Data URL',
                         abstract="Or provide a remote OpenDAP data URL,"
                                  " for example:"
                                  " http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2.dailyavgs/surface/mslp.2016.nc",  # noqa
                         min_occurs=0,
                         max_occurs=10,
                         supported_formats=[FORMATS.DODS]),
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
                          supported_formats=[FORMATS.NETCDF]),
        ]

        super(CDOEnsembles, self).__init__(
            self._handler,
            identifier="ensembles",
            title="CDO Ensembles Operations",
            abstract="Calling cdo to calculate ensembles operations.",
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
        datasets = []
        # append file urls
        if 'dataset' in request.inputs:
            for dataset in request.inputs['dataset']:
                datasets.append(dataset.file)
        # append opendap urls
        if 'dataset_opendap' in request.inputs:
            for dataset in request.inputs['dataset_opendap']:
                datasets.append(dataset.url)
        operator = request.inputs['operator'][0].data

        cdo = get_cdo()
        cdo_op = getattr(cdo, operator)

        outfile = os.path.join(self.workdir, 'cdo_{}.nc'.format(operator))
        cdo_op(input=datasets, output=outfile)

        response.outputs['output'].file = outfile
        response.update_status("cdo ensembles done", 100)
        return response
