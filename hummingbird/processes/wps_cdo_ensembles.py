"""
Processes with cdo ensemble opertions
"""
from cdo import Cdo
cdo_version = Cdo().version()

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format
from pywps.app.Common import Metadata

import logging
LOGGER = logging.getLogger("PYWPS")


class CDOEnsembles(Process):

    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Dataset',
                         abstract='You may provide a URL or upload a NetCDF file.',
                         metadata=[Metadata('Info')],
                         min_occurs=0,
                         max_occurs=100,
                         supported_formats=[Format('application/x-netcdf')]),
            LiteralInput('dataset_opendap', 'Remote OpenDAP Data URL',
                         data_type='string',
                         abstract="Or provide a remote OpenDAP data URL,"
                                  " for example:"
                                  " http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2.dailyavgs/surface/mslp.2016.nc",  # noqa
                         metadata=[
                            Metadata(
                                'application/x-ogc-dods',
                                'https://www.iana.org/assignments/media-types/media-types.xhtml')],
                         min_occurs=0,
                         max_occurs=100),
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
                datasets.append(dataset.data)
        operator = request.inputs['operator'][0].data

        cdo = Cdo()
        cdo_op = getattr(cdo, operator)

        outfile = 'cdo_{}.nc'.format(operator)
        cdo_op(input=datasets, output=outfile)

        response.outputs['output'].file = outfile
        response.update_status("cdo ensembles done", 100)
        return response
