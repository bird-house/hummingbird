"""
Processes with cdo commands
"""
from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format
from pywps.app.Common import Metadata

from hummingbird.utils import output_filename
from hummingbird.processing import cdo_version, get_cdo

import logging
LOGGER = logging.getLogger("PYWPS")


class CDOCopy(Process):
    """This process calls cdo with the copy operation on datasets (netcdf, opendap)"""
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Dataset',
                         abstract='You may provide a URL or upload a NetCDF file.',
                         min_occurs=0,
                         max_occurs=10,
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
                         max_occurs=10),
        ]
        outputs = [
            ComplexOutput('output', 'Output',
                          abstract="Copied and concatenated input datasets.",
                          as_reference=True,
                          supported_formats=[Format('application/x-netcdf')]),
        ]

        super(CDOCopy, self).__init__(
            self._handler,
            identifier="cdo_copy",
            title="CDO Copy",
            abstract="Calls CDO to copy or concatenate datasets."
                     " All input datasets need to have the same structure"
                     " with the same variables on different timesteps.",
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

        cdo = get_cdo()
        cdo_op = getattr(cdo, 'copy')

        outfile = output_filename(datasets[0], addition='copy', dir=self.workdir)
        cdo_op(input=datasets, output=outfile)

        response.outputs['output'].file = outfile
        response.update_status("cdo copy done", 100)
        return response
