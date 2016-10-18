import os
import shutil
from subprocess import check_output, CalledProcessError, STDOUT

from pywps.Process import WPSProcess
import logging
logger = logging.getLogger(__name__)


def cf_check(filename, version="auto"):
    # TODO: maybe use local file path
    if not filename.endswith(".nc"):
        new_name = filename + ".nc"
        from os import rename
        rename(filename, new_name)
        filename = new_name
    filename = os.path.abspath(filename)
    cmd = ["dkrz-cf-checker", filename]
    if version != "auto":
        cmd.extend(['-C', version])
    try:
        output = check_output(cmd)
    except CalledProcessError as err:
        logger.exception("cfchecks failed!")
        output = err.output
    return output


class CFChecker(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="qa_cfchecker",
            title="CF Checker by DKRZ",
            version="0.5.14",
            abstract="The NetCDF Climate Forcast Conventions compliance checker by DKRZ.\
             This process allows you to run the compliance checker to check that the contents of a NetCDF file comply\
             with the Climate and Forecasts (CF) Metadata Convention.\
             The CF Conformance checker applies to conventions 1.4 -1.7draft.\
             Development and maintenance for the CF-checker is done by the German Climate Computing Centre (DKRZ).\
             If you have suggestions for improvement then please contact\
             Heinz-Dieter Hollweg at DKRZ (hollweg@dkrz.de).",
            metadata=[
                {"title": "Documentation", "href": "http://qa-dkrz.readthedocs.io/en/latest/"},
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
            formats=[{"mimeType": "application/x-netcdf"}],
        )

        self.cf_version = self.addLiteralInput(
            identifier="cf_version",
            title="Check against CF version",
            abstract="Version of CF conventions that the NetCDF file should be check against.\
             Use auto to auto-detect the CF version.",
            default="auto",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=["auto", "1.6", "1.5", "1.4"],
        )

        self.output = self.addComplexOutput(
            identifier="output",
            title="CF Checker Report",
            abstract="Summary of the CF compliance check",
            formats=[{"mimeType": "text/plain"}],
            asReference=True,
        )

    def execute(self):
        self.status.set("starting cfchecker ...", 0)

        # TODO: iterate input files ... run parallel
        # TODO: generate html report with links to cfchecker output ...
        outfile = 'cfchecker_output.txt'
        self.output.setValue(outfile)
        nc_files = self.getInputValues(identifier='dataset')
        count = 0
        max_count = len(nc_files)
        step = 100.0 / max_count
        for nc_file in nc_files:
            cf_report = cf_check(nc_file, version=self.cf_version.getValue())
            with open(outfile, 'a') as fp:
                fp.write(cf_report)
                count = count + 1
                self.status.set("cfchecker: %d/%d" % (count, max_count), int(count * step))
        self.status.set("cfchecker: done", 100)
