"""
Processes with cdo commands
"""
import os
import tarfile
import tempfile

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format, FORMATS
from pywps.app.Common import Metadata

from hummingbird.utils import output_filename
from hummingbird.processing import cdo_version, get_cdo

import logging
LOGGER = logging.getLogger("PYWPS")


class CDOClimateIndices(Process):
    """This process calls cdo to calculate climate indices written to a netcdf file"""
    def __init__(self):
        inputs = [
            LiteralInput('operator', 'CDO Climate Indices Operator',
                         data_type='string',
                         abstract="Choose a CDO Operator. Example: eca_su (Summer days index per time period)."
                          " See the CDO documentation to lookup a description of the operators.",
                         metadata=[
                             Metadata("CDO Operators", 'https://code.zmaw.de/projects/cdo/embedded/index.html')
                         ],
                         min_occurs=1,
                         max_occurs=1,
                         default='eca_su',
                         allowed_values=[
                         'eca_cdd',      # Consecutive dry days index per time period
                         'eca_cfd',      # Consecutive frost days index per time period
                         'eca_csu',      # Consecutive summer days index per time period
                         'eca_cwd',      # Consecutive wet days index per time period
                         # 'eca_cwdi',   # Cold wave duration index wrt mean of reference period
                         # 'eca_cwfi',   # Cold-spell days index wrt 10th percentile of reference period
                         'eca_etr',      # Intra-period extreme temperature range
                         'eca_fd',       # Frost days index per time period
                         'eca_gsl',      # Thermal Growing season length index
                         'eca_hd',       # Heating degree days per time period
                         # 'eca_hwdi',   # Heat wave duration index wrt mean of reference period
                         # 'eca_hwfi',   # Warm spell days index wrt 90th percentile of reference period
                         'eca_id',       # Ice days index per time period
                         'eca_pd',       # Precipitation days index per time period
                         'eca_r10mm',    # Heavy precipitation days index per time period
                         'eca_r1mm',     # --> eca_rr1
                         'eca_r20mm',    # Very heavy precipitation days index per time period
                         # 'eca_r75p',   # Moderate wet days wrt 75th percentile of reference period
                         'eca_r75ptot',  # Precipitation percent due to R75p days
                         # 'eca_r90p',   # Wet days wrt 90th percentile of reference period
                         'eca_r90ptot',  # Precipitation percent due to R90p days
                         # 'eca_r95p',   # Very wet days wrt 95th percentile of reference period
                         'eca_r95ptot',  # Precipitation percent due to R95p days
                         # 'eca_r99p',   # Extremely wet days wrt 99th percentile of reference period
                         'eca_r99ptot',  # Precipitation percent due to R99p days
                         'eca_rr1',      # Wet days index per time period
                         'eca_rx1day',   # Highest one day precipitation amount per time period
                         'eca_rx5day',   # Highest five-day precipitation amount per time period
                         'eca_sdii',     # Simple daily intensity index per time period
                         'eca_su',       # Summer days index per time period
                         # 'eca_tg10p',  # Cold days percent wrt 10th percentile of reference period
                         # 'eca_tg90p',  # Warm days percent wrt 90th percentile of reference period
                         # 'eca_tn10p',  # Cold nights percent wrt 10th percentile of reference period
                         # 'eca_tn90p',  # Warm nights percent wrt 90th percentile of reference period
                         'eca_tr',       # Tropical nights index per time period
                         # 'eca_tx10p',    # Very cold days percent wrt 10th percentile of reference period
                         # 'eca_tx90p',    # Very warm days percent wrt 90th percentile of reference period
                         ]),
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
        ]
        outputs = [
            ComplexOutput('output', 'Output',
                          abstract="Climate indice written to a NetCDF file generated by CDO.",
                          as_reference=True,
                          supported_formats=[FORMATS.NETCDF]),
            ComplexOutput('output_all', 'All calculated Indices',
                          abstract="Tar archive containing the netCDF files",
                          as_reference=True,
                          supported_formats=[Format('application/x-tar')]
                          ),
        ]

        super(CDOClimateIndices, self).__init__(
            self._handler,
            identifier="cdo_indices",
            title="CDO Climate Indices",
            abstract="Calculates climate indices like summer days using CDO."
                     " Calls the Climate Data Operators (CDO) tool with a single dataset (NetCDF, OpenDAP) provided"
                     " and uses the chosen operator to calculate climate indices written to a NetCDF file.",
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
        response.update_status("starting cdo indice calculation ...", 0)
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
        # init cdo
        cdo = get_cdo()
        cdo_op = getattr(cdo, operator)

        try:
            tar = tarfile.open(os.path.join(self.workdir, "cdo_{0}.tar".format(operator)), "w")
            num_ds = len(datasets)
            for idx, ds in enumerate(datasets):
                outfile = output_filename(ds, addition=operator, dir=self.workdir)
                msg = "calculating cdo indice {0} on {1} ...".format(operator, os.path.basename(ds))
                progress = int(idx * 100.0 / num_ds) + 1
                LOGGER.debug('index = %s, max = %s, progress = %s', idx, num_ds, progress)
                response.update_status(msg, progress)
                cdo_op(input=ds, output=outfile)
                tar.add(outfile)
        finally:
            tar.close()

        response.outputs['output'].file = outfile
        response.outputs['output_all'].file = tar.name

        response.update_status("cdo indices done", 100)
        return response
