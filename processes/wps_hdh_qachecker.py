import os
import shutil
from subprocess import check_output, CalledProcessError, STDOUT

from pywps.Process import WPSProcess
import logging
logger = logging.getLogger(__name__)

qa_task = """
PROJECT_DATA={1}/{0}
QC_RESULTS=results
PROJECT={0}
QC_CONF={0}_qc.conf
"""

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


class CordexChecker(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "qa_checker",
            title = "QA DKRZ Checker",
            version = "0.5.3-1",
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
        self.status.set("starting cordex checker ...", 0)

        outfile = 'out.txt'
        self.output.setValue( outfile )

        report = cordex_check(self.project.getValue(), self.archive_path.getValue())
        
        with open(outfile, 'a') as fp:
            fp.write(report)
        self.status.set("cordex checker: done", 100)


        
