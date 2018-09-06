"""
Processes with cdo commands
"""
import imp

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format, FORMATS
from pywps.app.Common import Metadata

from hummingbird.processing import cdo_version, get_cdo

import logging
LOGGER = logging.getLogger("PYWPS")


def cdo_wrap(tmargs):
    cdo = get_cdo()
    cdo_op = getattr(cdo, tmargs[3])
    return cdo_op(tmargs[0], input=tmargs[1], output=tmargs[2])


class CDOinter_MPI(Process):

    def __init__(self):
        inputs = [
            ComplexInput('netcdf_file', 'NetCDF File',
                         abstract='You may provide a URL or upload a NetCDF file.',
                         min_occurs=1,
                         max_occurs=100,
                         supported_formats=[Format('application/x-netcdf')]),
            LiteralInput('operator', 'CDO Operator',
                         data_type='string',
                         abstract="Choose a CDO Operator",
                         default='remapbil',
                         min_occurs=0,
                         max_occurs=1,
                         allowed_values=['remapbil', 'remapbic', 'remapdis',
                                         'remapnn', 'remapcon', 'remapcon2', 'remaplaf']),
            LiteralInput('regr', 'Grid',
                         data_type='string',
                         abstract="Select an grid",
                         default='r360x180',
                         min_occurs=0,
                         max_occurs=1,
                         allowed_values=['r64x32', 'r32x16', 'r1024x512', 'r360x180', 'r480x241', 'custom']),
            LiteralInput('longitude', 'longitude',
                         data_type='string',
                         abstract="New nx Longitude",
                         default=None,
                         min_occurs=0,
                         max_occurs=1),
            LiteralInput('latitude', 'Latitude',
                         data_type='string',
                         abstract="New ny Latitude",
                         default=None,
                         min_occurs=0,
                         max_occurs=1),
            LiteralInput('multi', 'Serial or MP',
                         data_type='string',
                         abstract="Use Serial or Multiprocessing/Multithreads",
                         default='Serial',
                         min_occurs=0,
                         max_occurs=1,
                         allowed_values=['Serial', 'Multiprocessing', 'Multithreads']),
        ]

        outputs = [
            ComplexOutput('tarout', 'Result files',
                          abstract="Tar archive containing the netCDF result files",
                          as_reference=True,
                          supported_formats=[Format('application/x-tar')]),
            ComplexOutput('output', 'Output',
                          abstract="One regrided file.",
                          as_reference=True,
                          supported_formats=[Format('application/x-netcdf')]),
        ]

        super(CDOinter_MPI, self).__init__(
            self._handler,
            identifier="cdo_inter_mpi",
            title="CDO Remapping",
            abstract="CDO Remapping of NetCDF File(s) with multiprocessing",
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
        import tarfile
        import os
        import tempfile

        nc_files = []
        for dataset in request.inputs['netcdf_file']:
            nc_files.append(dataset.file)

        (fp_tarf, tarf) = tempfile.mkstemp(dir=".", suffix='.tar')
        tar = tarfile.open(tarf, "w")

        operator = request.inputs['operator'][0].data
        response.update_status("starting cdo %s operator" % (operator), 10)

        gri = request.inputs['regr'][0].data   # here also should be checked default values!

        if (gri == 'custom'):
            try:
                gri = 'r' + str(request.inputs['longitude'][0].data) + 'x' + str(request.inputs['latitude'][0].data)
                LOGGER.debug('Using custom grid GRI = %s' % (gri))
            except Exception:
                gri = str(request.inputs['regr'][0].default)   # Should be checked (!)
                LOGGER.debug('Custom grid is not well specified, using default GRI = %s' % (gri))

        LOGGER.debug('GRI = %s' % (gri))

        try:
            Multi = str(request.inputs['multi'][0].data)
        except Exception:
            Multi = str(request.inputs['multi'][0].default)

        try:
            imp.find_module('multiprocessing')
        except ImportError:
            Multi = 'Serial'

        LOGGER.debug('Used calc type: = %s' % (Multi))

        #  ------------------------- For Multi Proc

        if ('Serial' not in Multi):

            if ('threads' not in Multi):
                from multiprocessing import Pool
                pool = Pool()
            else:
                from multiprocessing.dummy import Pool as ThreadPool
                pool = ThreadPool()

            outfiles = []
            new_arc_names = []
            grids = [gri] * len(nc_files)
            operators = [operator] * len(nc_files)

            for nc_file in nc_files:
                (fp_ncf, outfile) = tempfile.mkstemp(dir=".", suffix='.nc')
                LOGGER.debug('Input NetCDF file = %s' % (nc_file))
                outfiles.append(outfile)

                new_arc_name = os.path.basename(nc_file.split(".nc")[0] + "_" + operator + "_" + gri + ".nc")
                LOGGER.debug('NEW NAME for Output NetCDF file = %s' % (new_arc_name))
                new_arc_names.append(new_arc_name)

            args = zip(grids, nc_files, outfiles, operators)
            # res = pool.map(cdo_wrap, args)
            pool.map(cdo_wrap, args)
            pool.close()
            pool.join()

            for i, outfn in enumerate(outfiles):
                tar.add(outfn, arcname=new_arc_names[i])

        else:   # ------------------ if Serial
            cdo = get_cdo()
            cdo_op = getattr(cdo, operator)

            for nc_file in nc_files:
                (fp_ncf, outfile) = tempfile.mkstemp(dir=".", suffix='.nc')
                LOGGER.debug('Input NetCDF file = %s' % (nc_file))
                cdo_op(gri, input=nc_file, output=outfile)

                new_arc_name = os.path.basename(nc_file.split(".nc")[0] + "_" + operator + "_" + gri + ".nc")

                LOGGER.debug('NEW NAME for Output NetCDF file = %s' % (new_arc_name))
                tar.add(outfile, arcname=new_arc_name)

        tar.close()
        response.outputs['output'].file = outfile
        response.outputs['tarout'].file = tarf
        response.update_status("cdo remapping done", 100)
        return response
