import os
import tarfile

from compliance_checker.runner import ComplianceChecker, CheckSuite
from compliance_checker import __version__ as cchecker_version

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import Format, FORMATS
from pywps.app.Common import Metadata

import logging
LOGGER = logging.getLogger("PYWPS")


class IOOSCChecker(Process):
    def __init__(self):
        inputs = [
            LiteralInput('test', 'Test Suite',
                         data_type='string',
                         abstract="Select the test you want to run."
                                  " Default: cf (climate forecast conventions)",
                         min_occurs=1,
                         max_occurs=1,
                         default='cf',
                         allowed_values=['cf', 'ioos']),
            LiteralInput('criteria', 'Criteria',
                         data_type='string',
                         abstract="Define the criteria for the checks.  Either Strict, Normal or Lenient."
                                  " Defaults to Normal.",
                         min_occurs=1,
                         max_occurs=1,
                         default='normal',
                         allowed_values=['strict', 'normal', 'lenient']),
            ComplexInput('dataset', 'NetCDF File',
                         abstract='You may provide a URL or upload a NetCDF file.',
                         metadata=[Metadata('Info')],
                         min_occurs=0,
                         max_occurs=100,
                         supported_formats=[Format('application/x-netcdf')]),
            LiteralInput('dataset_opendap', 'Remote OpenDAP Data URL',
                         data_type='string',
                         abstract="Or provide a remote OpenDAP data URL,"
                                  " for example:"
                                  " http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2.dailyavgs/surface/mslp.2016.nc",  # noqa
                         min_occurs=0,
                         max_occurs=100),
            LiteralInput('format', 'Output Format',
                         data_type='string',
                         abstract="The format of the check reporst. Either text, json or html. Defaults to html.",
                         min_occurs=1,
                         max_occurs=1,
                         default='html',
                         allowed_values=['text', 'json', 'html']),
        ]

        outputs = [
            ComplexOutput('output', 'Summary Report',
                          abstract="Summary report of check results.",
                          as_reference=True,
                          supported_formats=[Format('text/plain')]),
            ComplexOutput('report', 'Check Report',
                          abstract="Report of check result.",
                          as_reference=True,
                          supported_formats=[Format('text/html')]),
            ComplexOutput('report_tar', 'Reports as tarfile',
                          abstract="Report of check result for each file as tarfile.",
                          as_reference=True,
                          supported_formats=[Format('application/x-tar')]),
        ]

        super(IOOSCChecker, self).__init__(
            self._handler,
            identifier="ioos_cchecker",
            title="IOOS Compliance Checker",
            version=cchecker_version,
            abstract="The IOOS Compliance Checker is a Python tool to"
                     " check local/remote datasets against a variety of"
                     " compliance standards. Each compliance standard is executed"
                     " by a Check Suite, which functions similar to a"
                     " Python standard Unit Test."
                     " A Check Suite runs one or more checks against a dataset,"
                     " returning a list of Results which are then aggregated"
                     " into a summary. Development and maintenance for the compliance"
                     " checker is done by the Integrated Ocean Observing System (IOOS).",
            metadata=[
                Metadata('Birdhouse', 'http://bird-house.github.io/'),
                Metadata('User Guide', 'http://birdhouse-hummingbird.readthedocs.io/en/latest/'),
                Metadata('CF Conventions', 'http://cfconventions.org/'),
                Metadata('IOOS', 'https://ioos.noaa.gov/'),
                Metadata('Compliance Checker on GitHub', 'https://github.com/ioos/compliance-checker'),
                Metadata('IOOS Compliance Online Checker', 'http://data.ioos.us/compliance/index.html'),
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

        output_format = request.inputs['format'][0].data

        max_count = len(datasets)
        step = 100.0 / max_count

        # patch check_suite
        from hummingbird.patch import patch_compliance_checker
        patch_compliance_checker()
        # patch end

        check_suite = CheckSuite()
        check_suite.load_all_available_checkers()

        # output
        os.mkdir("report")
        # response.outputs['report'].output_format = FORMATS.TEXT
        response.outputs['report'].file = "report/0.{0}".format(output_format)

        with open('report/summary.txt', 'w') as fp:
            response.outputs['output'].output_format = FORMATS.TEXT
            response.outputs['output'].file = fp.name
            for idx, ds in enumerate(datasets):
                LOGGER.info("checking dataset %s", ds)
                report_file = "report/{0}.{1}".format(idx, output_format)
                return_value, errors = ComplianceChecker.run_checker(
                    ds,
                    checker_names=[checker.data for checker in request.inputs['test']],
                    verbose=True,
                    criteria=request.inputs['criteria'][0].data,
                    output_filename=report_file,
                    output_format=output_format)
                if return_value is False:
                    LOGGER.info("dataset %s with errors %s" % (ds, errors))
                    fp.write("{0}, FAIL, {1}\n".format(ds, report_file))
                else:
                    fp.write("{0}, PASS, {1}\n".format(ds, report_file))
                response.update_status("checks: %d/%d" % (idx, max_count), int(idx * step))
        with tarfile.open("report.tar", "w") as tar:
            # response.outputs['report_tar'].output_format = FORMATS.TEXT
            response.outputs['report_tar'].file = tar.name
            tar.add("report")

        response.update_status("compliance checker finshed.", 100)
        return response
