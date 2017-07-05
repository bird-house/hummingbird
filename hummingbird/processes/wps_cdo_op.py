"""
Processes with cdo commands
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


class CDOOperation(Process):
    """This process calls cdo with operation on netcdf file"""
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Dataset',
                         abstract='You may provide a URL or upload a NetCDF file.',
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
            LiteralInput('operator', 'CDO Operator',
                         data_type='string',
                         abstract="Choose a CDO Operator.\
                          See the CDO documentation to lookup a description of the operators.",
                         metadata=[
                             Metadata("CDO Operators", 'https://code.zmaw.de/projects/cdo/embedded/index.html')
                         ],
                         min_occurs=1,
                         max_occurs=1,
                         default='monmax',
                         allowed_values=[
                             'merge', 'dayavg', 'daymax', 'daymean', 'daymin',
                             'daysum', 'dayvar', 'daystd', 'monmax', 'monmin',
                             'monmean', 'monavg', 'monsum', 'monvar', 'monstd',
                             'ymonmin', 'ymonmax', 'ymonsum', 'ymonmean', 'ymonavg',
                             'ymonvar', 'ymonstd', 'yearavg', 'yearmax', 'yearmean',
                             'yearmin', 'yearsum', 'yearvar', 'yearstd', 'yseasvar']),
        ]
        outputs = [
            ComplexOutput('output', 'Output',
                          abstract="NetCDF Output generated by CDO.",
                          as_reference=True,
                          supported_formats=[Format('application/x-netcdf')]),
        ]

        super(CDOOperation, self).__init__(
            self._handler,
            identifier="cdo_operation",
            title="CDO Operation",
            abstract="Calls CDO operations like monmax on a NetCDF file.",
            version=cdo_version,
            metadata=[
                Metadata('User Guide', 'http://birdhouse-hummingbird.readthedocs.io/en/latest/'),
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
        response.update_status("cdo operator done", 100)
        return response
