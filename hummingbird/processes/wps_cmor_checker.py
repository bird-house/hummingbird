import os
import tarfile

from hummingbird.processing import cmor_checker, cmor_tables

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format, FORMATS
from pywps.app.Common import Metadata

import logging
LOGGER = logging.getLogger("PYWPS")


class CMORChecker(Process):
    def __init__(self):
        inputs = [
            LiteralInput('variable', 'Variable',
                         data_type='string',
                         abstract="Specify geophysical variable name. (Optional)",
                         min_occurs=0,
                         max_occurs=1),
            # LiteralInput('cmip6_table', 'CMIP6 Table',
            #              data_type='string',
            #              abstract="CMIP6 CMOR table name, ex: CMIP6_CV.",
            #              min_occurs=1,
            #              max_occurs=1,
            #              default='CMIP6_CV',
            #              allowed_values=cmor_tables()),
            ComplexInput('dataset', 'Dataset',
                         abstract='You may provide a URL or upload a NetCDF file.',
                         metadata=[Metadata('Info')],
                         min_occurs=1,
                         max_occurs=1024,
                         supported_formats=[Format('application/x-netcdf')]),
            # LiteralInput('dataset_opendap', 'Remote OpenDAP Data URL',
            #              data_type='string',
            #              abstract="Or provide a remote OpenDAP data URL,"
            #                       " for example:"
            #                       " http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2.dailyavgs/surface/mslp.2016.nc",  # noqa
            #              metadata=[
            #                 Metadata(
            #                     'application/x-ogc-dods',
            #                     'https://www.iana.org/assignments/media-types/media-types.xhtml')],
            #              min_occurs=0,
            #              max_occurs=100),
        ]

        outputs = [
            ComplexOutput('output', 'Summary Report',
                          abstract="Summary report of check results.",
                          as_reference=True,
                          supported_formats=[Format('text/plain')]),
            ComplexOutput('report', 'Check Report',
                          abstract="Report of check result.",
                          as_reference=True,
                          supported_formats=[Format('text/plain')]),
            ComplexOutput('report_tar', 'Reports as tarfile',
                          abstract="Report of check result for each file as tarfile.",
                          as_reference=True,
                          supported_formats=[Format('application/x-tar')]),
        ]

        super(CMORChecker, self).__init__(
            self._handler,
            identifier="cmor_checker",
            title="CMIP6 CMOR Checker",
            version="3.2.2",
            abstract='Calls the CMIP6 cmor checker to verify CMIP6 compliance.'
                     'CMIP6 CMOR checker will verify that all attributes in the input file are present'
                     ' and conform to CMIP6 for publication into ESGF.',
            metadata=[
                Metadata('CMOR Checker on GitHub', 'https://github.com/PCMDI/cmor'),
                Metadata('User Guide', 'https://cmor.llnl.gov/mydoc_cmip6_validator/'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        # TODO: iterate input files ... run parallel
        # TODO: generate html report with links to cfchecker output ...
        datasets = []
        if 'dataset' in request.inputs:
            for dataset in request.inputs['dataset']:
                datasets.append(dataset.file)
        # append opendap urls
        if 'dataset_opendap' in request.inputs:
            for dataset in request.inputs['dataset_opendap']:
                datasets.append(dataset.data)
        if 'variable' in request.inputs:
            variable = request.inputs['variable'][0].data
        else:
            variable = None

        max_count = len(datasets)
        step = 100.0 / max_count

        # output
        os.mkdir("report")
        with open('report/summary.txt', 'w') as fp:
            response.outputs['output'].file = fp.name
            for idx, ds in enumerate(datasets):
                dataset_id = os.path.basename(ds)
                LOGGER.info("checking dataset %s", dataset_id)
                report_file = "report/{0}.txt".format(dataset_id)
                response.outputs['report'].file = report_file
                return_value = cmor_checker(
                    ds,
                    variable=variable,
                    cmip6_table="CMIP6_CV",
                    output_filename=report_file)
                if return_value is False:
                    LOGGER.info("dataset check %s with errors.", dataset_id)
                    fp.write("{0}, FAIL\n".format(dataset_id))
                else:
                    fp.write("{0}, PASS\n".format(dataset_id))
                response.update_status("checks: %d/%d" % (idx, max_count), int(idx * step))
        with tarfile.open("report.tar", "w") as tar:
            response.outputs['report_tar'].file = tar.name
            tar.add("report")

        response.update_status("cmor checker finshed.", 100)
        return response
