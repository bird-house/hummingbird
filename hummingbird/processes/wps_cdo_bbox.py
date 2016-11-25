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


class CDOBBox(Process):
    """This process calls cdo sellonlatbox on netcdf file"""
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'NetCDF File',
                         abstract='You may provide a URL or upload a NetCDF file.',
                         metadata=[Metadata('Info')],
                         min_occurs=1,
                         max_occurs=100,
                         supported_formats=[Format('application/x-netcdf')]),
            LiteralInput('bbox', 'Bounding Box',
                         data_type='string',
                         abstract="Enter a bbox: min_lon, max_lon, min_lat, max_lat.\
                            min_lon=Western longitude,\
                            max_lon=Eastern longitude,\
                            min_lat=Southern or northern latitude,\
                            max_lat=Northern or southern latitude.\
                            For example: 0,20,40,60 ",
                         min_occurs=1,
                         max_occurs=1,
                         default='0,20,40,60 ',
                         ),
        ]
        outputs = [
            ComplexOutput('output', 'NetCDF Output',
                          abstract="CDO sellonlatbox result.",
                          as_reference=True,
                          supported_formats=[Format('application/x-netcdf')]),
        ]

        super(CDOBBox, self).__init__(
            self._handler,
            identifier="cdo_bbox",
            title="CDO select lon/lat box",
            abstract="Apply CDO sellonlatbox on a NetCDF File.",
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
        bbox = request.inputs['bbox'][0].data

        cdo = Cdo()

        outfile = 'out.nc'
        cdo.sellonlatbox(bbox, input=datasets[0], output=outfile)

        response.outputs['output'].file = outfile
        response.update_status("cdo bbox done", 100)
        return response
