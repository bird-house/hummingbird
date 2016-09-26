import os
import shutil
import tarfile
import glob
from subprocess import check_output, CalledProcessError, STDOUT

from pywps.Process import WPSProcess

import logging
logger = logging.getLogger(__name__)

def qa_checker(filename, project, qa_home=None):
    cmd = ["qa-dkrz", "-P", project]
    if qa_home:
        cmd.append("--work="+qa_home)
    cmd.append(filename)
    try:
        output = check_output(cmd, stderr=STDOUT)
    except CalledProcessError as e:
        msg = "qa checker failed: %s" % (e.output)
        logger.error(msg)
        raise Exception(msg)


class QualityChecker(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "qa_checker",
            title = "Quality Assurance Checker by DKRZ",
            version = "0.5.14",
            abstract="The Quality Assurance checker QA-DKRZ checks conformance of meta-data of climate simulations given in NetCDF format with conventions and rules of climate model projects. At present, checking of CF Conventions, CMIP5, and CORDEX is supported. Development and maintenance for the QA checker is done by the German Climate Computing Centre (DKRZ). If you have suggestions for improvement then please contact Heinz-Dieter Hollweg at DKRZ (hollweg@dkrz.de).",
            metadata= [
                {"title": "Documentation" , "href": "http://qa-dkrz.readthedocs.io/en/latest/"},
                {"title": "CF Conventions", "href": "http://cfconventions.org/"},
                {"title": "Conda Package", "href": "http://anaconda.org/birdhouse/qa-dkrz"},
                {"title": "GitHub", "href": "https://github.com/IS-ENES-Data/QA-DKRZ"}, ],
            statusSupported=True,
            storeSupported=True
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="URL to your NetCDF File",
            abstract="You may provide a URL or upload a NetCDF file.",
            minOccurs=1,
            maxOccurs=100,
            maxmegabites=10000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.project = self.addLiteralInput(
            identifier="project",
            title="Project",
            abstract="Climate model data project to be checked: CORDEX or CMIP5",
            default="CORDEX",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['CORDEX', 'CMIP5'])

        self.output = self.addComplexOutput(
            identifier="output",
            title="Quality Checker Report",
            abstract="Qualtiy checker results as tar archive.",
            formats=[{"mimeType":"application/x-tar-gz"}],
            asReference=True,
            )

        self.logfile = self.addComplexOutput(
            identifier="logfile",
            title="Quality Checker Logfile",
            abstract="Qualtiy checker summary logfile",
            formats=[{"mimeType":"text/yaml"}],
            asReference=True,
            )

    def execute(self):
        from hummingbird import config
        from hummingbird import utils

        self.status.set("starting qa checker ...", 0)

        # create qa_home
        qa_home = os.path.join(config.cache_path(), "qa_dkrz")
        utils.make_dirs(qa_home)

        datasets = self.getInputValues(identifier='dataset')
        for idx,ds in enumerate(datasets):
            progress = idx * 100 / len(datasets)
            self.status.set("checking %s" % ds, progress)
            qa_checker(ds, project=self.project.getValue(), qa_home=qa_home)

        results_path = os.path.join("QA_Results", "check_logs")
        if not os.path.isdir(results_path):
            raise Exception("QA results are missing.")

        # output tar archive
        outfile = 'output.tar.gz'
        self.output.setValue( outfile )
        tar = tarfile.open(outfile, "w:gz")
        tar.add(results_path)
        tar.close()

        # output logfile
        logs = glob.glob(os.path.join(results_path, "*.log"))
        if not logs:
            logs = glob.glob(os.path.join(results_path, ".*.log"))
        if logs:
            # use .txt extension
            filename = logs[0][:-4] + '.txt'
            os.link(logs[0], filename)
            self.logfile.setValue(filename)
        else:
            raise Exception("could not find log file.")

        self.status.set("qa checker: done", 100)
