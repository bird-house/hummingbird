import os
from pywps import Process
from pywps import ComplexInput, ComplexOutput
from pywps import FORMATS
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from hummingbird.processing import ncdump, ncgen

import logging
LOGGER = logging.getLogger("PYWPS")


class NCDump(Process):
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Dataset',
                         abstract='Enter a URL pointing to a NetCDF file (optional)',
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
        ]
        outputs = [
            ComplexOutput('output', 'NetCDF Metadata',
                          abstract='NetCDF Metadata',
                          as_reference=True,
                          supported_formats=[FORMATS.TEXT]),
            ComplexOutput('ncgen', 'NetCDF file generated from Metadata',
                          abstract='NetCDF file generated from Metadata',
                          as_reference=True,
                          supported_formats=[FORMATS.NETCDF]),
        ]

        super(NCDump, self).__init__(
            self._handler,
            identifier="ncdump",
            title="NCDump",
            version="4.7.3",
            abstract="Run ncdump to retrieve NetCDF header metadata.",
            metadata=[
                Metadata('Birdhouse', 'http://bird-house.github.io/'),
                Metadata('User Guide', 'http://birdhouse-hummingbird.readthedocs.io/en/latest/')],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True)

    def _handler(self, request, response):
        if 'dataset_opendap' in request.inputs:
            dataset = request.inputs['dataset_opendap'][0].url
        elif 'dataset' in request.inputs:
            dataset = request.inputs['dataset'][0].file
        else:
            raise ProcessError("You need to provide a Dataset.")

        cdl_file = os.path.join(self.workdir, "nc_dump.cdl")
        with open(cdl_file, 'w') as fp:
            fp.writelines(ncdump(dataset))
            response.outputs['output'].output_format = FORMATS.TEXT
            response.outputs['output'].file = fp.name
        output_file = os.path.join(self.workdir, "nc_dump.nc")
        ncgen(cdl_file, output_file)
        response.outputs['ncgen'].output_format = FORMATS.NETCDF
        response.outputs['ncgen'].file = output_file
        response.update_status('done', 100)
        return response
