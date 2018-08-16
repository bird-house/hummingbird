"""
Processes with cdo commands
"""
import os.path

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format
from pywps.app.Common import Metadata

from hummingbird.processing import cdo_version, get_cdo

import logging
LOGGER = logging.getLogger("PYWPS")


class CDOInfo(Process):
    """This process calls cdo sinfo on netcdf file"""
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
            abstract="Runs CDO to retrieve NetCDF metadata information."
                     " Calls the sinfo operator of CDO (Climate Data Operator) on a NetCDF file"
                     " and returns a document with metadata information.",
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

        outfile = os.path.join(self.workdir, 'cdo_sinfo.txt')
        with open(outfile, 'w') as fp:
            response.outputs['output'].file = outfile
            for ds in datasets:
                sinfo = cdo.sinfo(input=[ds], output=outfile)
                for line in sinfo:
                    fp.write(line + '\n')
                fp.write('\n\n')
        response.update_status("cdo sinfo done", 100)
        return response
