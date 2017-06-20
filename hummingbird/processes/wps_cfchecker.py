import os
from subprocess import check_output, CalledProcessError

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format
from pywps.app.Common import Metadata

import logging
LOGGER = logging.getLogger("PYWPS")


def cf_check(nc_file, version):
    # TODO: avoid downloading of cf table for each check (see pypi page)
    LOGGER.debug("checking %s", os.path.basename(nc_file))
    if not nc_file.endswith(".nc"):
        new_name = nc_file + ".nc"
        os.rename(nc_file, new_name)
        nc_file = new_name
    cmd = ["cfchecks", "--version", version, nc_file]
    try:
        cf_report = check_output(cmd)
    except CalledProcessError as err:
        LOGGER.warn("cfchecks failed!")
        cf_report = err.output
    return cf_report


class CFChecker(Process):
    def __init__(self):
        inputs = [
            LiteralInput('cf_version', 'Check against CF version',
                         data_type='string',
                         abstract="Version of CF conventions that the NetCDF file should be check against."
                                  " Use auto to auto-detect the CF version.",
                         min_occurs=1,
                         max_occurs=1,
                         default='auto',
                         allowed_values=["auto", "1.6", "1.5", "1.4", "1.3", "1.2", "1.1", "1.0"]),
            ComplexInput('dataset', 'Dataset',
                         abstract='You may provide a URL or upload a NetCDF file.',
                         metadata=[Metadata('Info')],
                         min_occurs=0,
                         max_occurs=1024,
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
                         max_occurs=1024),
        ]
        outputs = [
            ComplexOutput('output', 'CF Checker Report',
                          abstract="Summary of the CF compliance check",
                          as_reference=True,
                          supported_formats=[Format('text/plain')]),
        ]

        super(CFChecker, self).__init__(
            self._handler,
            identifier="cfchecker",
            title="CF Checker by NCAS Computational Modelling Services (NCAS-CMS)",
            version="3.0.5",
            abstract="The NetCDF Climate Forcast Conventions compliance checker by CEDA."
                     " This process allows you to run the compliance checker"
                     " to check that the contents of a NetCDF file comply"
                     " with the Climate and Forecasts (CF) Metadata Convention."
                     " The CF-checker was developed at the Hadley Centre for Climate Prediction and Research,"
                     " UK Met Office by Rosalyn Hatcher."
                     " This work was supported by PRISM (PRogramme for Integrated Earth System Modelling)."
                     " Development and maintenance for the CF-checker has now been taken over by the"
                     " NCAS Computational Modelling Services (NCAS-CMS)."
                     " If you have suggestions for improvement then please contact"
                     " Rosalyn Hatcher at NCAS-CMS (r.s.hatcher@reading.ac.uk).",
            metadata=[
                Metadata('User Guide', 'http://birdhouse-hummingbird.readthedocs.io/en/latest/'),
                Metadata('Readme on PyPI', 'https://pypi.python.org/pypi/cfchecker/3.0.4'),
                Metadata('CF Conventions', 'http://cfconventions.org/'),
                Metadata('Online Compliance Checker', 'http://cfconventions.org/compliance-checker.html'),
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

        count = 0
        max_count = len(datasets)
        step = 100.0 / max_count
        for dataset in datasets:
            cf_report = cf_check(dataset, version=request.inputs['cf_version'][0].data)
            with open('cfchecker_output.txt', 'a') as fp:
                response.outputs['output'].file = fp.name
                fp.write(cf_report + "\n\n")
                count = count + 1
                response.update_status("cfchecker: %d/%d" % (count, max_count), int(count * step))
        response.update_status("cfchecker done.", 100)
        return response
