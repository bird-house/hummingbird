import os
import shutil
from subprocess import check_output, CalledProcessError, STDOUT

from pywps.Process import WPSProcess
from malleefowl.process import show_status, getInputValues, mktempfile

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

qa_task = """
PROJECT_DATA={1}/{0}
QC_RESULTS=results
PROJECT={0}
QC_CONF={0}_qc.conf
"""

def cf_check(nc_file):
    logger.debug("start cf_check: nc_file=%s", nc_file)
    # TODO: maybe use local file path
    if not nc_file.endswith(".nc"):
        new_name = nc_file + ".nc"
        from os import rename
        rename(nc_file, new_name)
        nc_file = new_name
    cmd = ["dkrz-cf-checker", nc_file]
    try:
        output = check_output(cmd)
    except CalledProcessError as err:
        logger.exception("cfchecks failed!")
        output = err.output
    return output

def cordex_check(project, archive_path):
    # generate task config
    with open("qa.task", 'w') as fp:
        fp.write(qa_task.format(project, archive_path))

    # run checker    
    cmd = ["qa-dkrz", "-m", "-f", "qa.task"]
    try:
        output = check_output(cmd, stderr=STDOUT)
    except CalledProcessError as err:
        logger.exception("cordex check failed!")
        output = err.output
    return output

class CFChecker(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier="qa_cfchecker",
            title="QA DKRZ CF Checker",
            version="0.5.2-1",
            abstract="Qualtiy Assurance Tools by DKRZ: cfchecker checks NetCDF files for compliance to the CF standard.",
            statusSupported=True,
            storeSupported=True
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="Dataset (NetCDF)",
            minOccurs=1,
            maxOccurs=1000,
            maxmegabites=10000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.output=self.addComplexOutput(
            identifier="output",
            title="CF Checker Report",
            abstract="",
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        show_status(self, "starting cfchecker ...", 0)

        # TODO: iterate input files ... run parallel 
        # TODO: generate html report with links to cfchecker output ...
        outfile = mktempfile(suffix='.txt')
        self.output.setValue( outfile )
        nc_files = getInputValues(self, identifier='dataset')
        count = 0
        max_count = len(nc_files)
        step = 100.0 / max_count
        for nc_file in nc_files:
            cf_report = cf_check(nc_file)
            with open(outfile, 'a') as fp:
                fp.write(cf_report)
                count = count + 1
                show_status(self, "cfchecker: %d/%d" % (count, max_count), int(count*step))
        show_status(self, "cfchecker: done", 100)


class CordexChecker(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "qa_checker",
            title = "QA DKRZ Checker",
            version = "0.5.2-1",
            abstract="Qualtiy Assurance Tools by DKRZ: project specific checks for cordex, cmip5, ...",
            statusSupported=True,
            storeSupported=True
            )

        self.project = self.addLiteralInput(
            identifier="project",
            title="Project",
            default="CORDEX",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['CORDEX'])

        self.archive_path = self.addLiteralInput(
            identifier="archive_path",
            title="Path to data archive",
            default="",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Cordex Checker Report",
            abstract="",
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        show_status(self, "starting cordex checker ...", 0)

        outfile = mktempfile(suffix='.txt')
        self.output.setValue( outfile )

        report = cordex_check(self.project.getValue(), self.archive_path.getValue())
        
        with open(outfile, 'a') as fp:
            fp.write(report)
        show_status(self, "cordex checker: done", 100)


        
