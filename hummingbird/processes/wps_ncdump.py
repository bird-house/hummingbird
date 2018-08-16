import os
from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format, FORMATS
from pywps.app.Common import Metadata

from hummingbird.processing import ncdump

import logging
LOGGER = logging.getLogger("PYWPS")


class NCDump(Process):
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Dataset',
                         abstract='Enter a URL pointing to a NetCDF file (optional)',
                         min_occurs=0,
                         max_occurs=100,
                         supported_formats=[Format('application/x-netcdf')]),
            LiteralInput('dataset_opendap', 'Remote OpenDAP Data URL',
                         data_type='string',
                         abstract="Or provide a remote OpenDAP data URL,"
                                  " for example: http://my.opendap/thredds/dodsC/path/to/file.nc",
                         metadata=[
                             Metadata(
                                 'application/x-ogc-dods',
                                 'https://www.iana.org/assignments/media-types/media-types.xhtml')],
                         min_occurs=0,
                         max_occurs=100),
        ]
        outputs = [
            ComplexOutput('output', 'NetCDF Metadata',
                          abstract='NetCDF Metadata',
                          as_reference=True,
                          supported_formats=[Format('text/plain')]),
        ]

        super(NCDump, self).__init__(
            self._handler,
            identifier="ncdump",
            title="NCDump",
            version="4.6.1",
            abstract="Run ncdump to retrieve NetCDF header metadata.",
            metadata=[
                Metadata('Birdhouse', 'http://bird-house.github.io/'),
                Metadata('User Guide', 'http://birdhouse-hummingbird.readthedocs.io/en/latest/')],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True)

    def _handler(self, request, response):
        datasets = []
        # append file url
        if 'dataset' in request.inputs:
            for dataset in request.inputs['dataset']:
                datasets.append(dataset.file)
        # append opendap urls
        if 'dataset_opendap' in request.inputs:
            for dataset in request.inputs['dataset_opendap']:
                datasets.append(dataset.data)

        count = 0
        with open(os.path.join(self.workdir, "nc_dump.txt"), 'w') as fp:
            response.outputs['output'].output_format = FORMATS.TEXT
            response.outputs['output'].file = fp.name
            for dataset in datasets:
                response.update_status("running ncdump", int(count * 100.0 / len(datasets)))
                fp.writelines(ncdump(dataset))
                count = count + 1
        response.update_status('compliance checker finshed...', 100)
        return response
