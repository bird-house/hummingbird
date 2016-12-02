import os
import shutil
import tarfile
import glob

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format, FORMATS
from pywps.app.Common import Metadata

import logging
LOGGER = logging.getLogger("PYWPS")


class QualityChecker(Process):
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'NetCDF File',
                         abstract='You may provide a URL or upload a NetCDF file.',
                         metadata=[Metadata('Info')],
                         min_occurs=1,
                         max_occurs=100,
                         supported_formats=[Format('application/x-netcdf')]),
            LiteralInput('project', 'Project',
                         data_type='string',
                         abstract="Climate model data project to be checked: CORDEX or CMIP5",
                         min_occurs=1,
                         max_occurs=1,
                         default='auto',
                         allowed_values=['CORDEX', 'CMIP5']),
        ]
        outputs = [
            ComplexOutput('output', 'Quality Checker Report',
                          abstract="Qualtiy checker results as tar archive.",
                          as_reference=True,
                          supported_formats=[Format('application/x-tar-gz')]),
            ComplexOutput('logfile', 'Quality Checker Logfile',
                          abstract="Qualtiy checker summary logfile",
                          as_reference=True,
                          supported_formats=[Format('text/yaml')]),
        ]

        super(QualityChecker, self).__init__(
            self._handler,
            identifier="qa_checker",
            title="Quality Assurance Checker by DKRZ",
            version="0.6.0",
            abstract="The Quality Assurance checker QA-DKRZ checks conformance of meta-data of climate simulations\
                given in NetCDF format with conventions and rules of climate model projects.\
                At present, checking of CF Conventions, CMIP5, and CORDEX is supported.\
                Development and maintenance for the QA checker is done by the German Climate Computing Centre (DKRZ).\
                If you have suggestions for improvement then please contact\
                Heinz-Dieter Hollweg at DKRZ (hollweg@dkrz.de).",
            metadata=[
                Metadata('Birdhouse', 'http://bird-house.github.io/'),
                Metadata('User Guide', 'http://birdhouse-hummingbird.readthedocs.io/en/latest/'),
                Metadata('CF Conventions', 'http://cfconventions.org/'),
                Metadata('QA Checker Documentation', 'http://qa-dkrz.readthedocs.io/en/latest/'),
                Metadata('Conda Package', 'http://anaconda.org/birdhouse/qa-dkrz'),
                Metadata('GitHub', 'https://github.com/IS-ENES-Data/QA-DKRZ'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        from hummingbird.processing import hdh_qa_checker

        response.update_status("starting qa checker ...", 0)

        # create qa_home
        # qa_home = os.path.join(config.cache_path(), "qa_dkrz")
        qa_home = os.path.abspath("./qa_dkrz")
        os.makedirs(qa_home)

        datasets = [dataset.file for dataset in request.inputs['dataset']]
        for idx, ds in enumerate(datasets):
            progress = idx * 100 / len(datasets)
            response.update_status("checking %s" % ds, progress)
            hdh_qa_checker(ds, project=request.inputs['project'][0].data, qa_home=qa_home)

        results_path = os.path.join("QA_Results", "check_logs")
        if not os.path.isdir(results_path):
            raise Exception("QA results are missing.")

        # output tar archive
        with tarfile.open('output.tar.gz', "w:gz") as tar:
            response.outputs['output'].file = tar.name
            tar.add(results_path)

        # output logfile
        logs = glob.glob(os.path.join(results_path, "*.log"))
        if not logs:
            logs = glob.glob(os.path.join(results_path, ".*.log"))
        if logs:
            # use .txt extension
            filename = logs[0][:-4] + '.txt'
            os.link(logs[0], filename)
            response.outputs['logfile'].file = filename
        else:
            raise Exception("could not find log file.")

        response.update_status("qa checker done.", 100)
        return response
